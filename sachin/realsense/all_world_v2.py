import pyrealsense2 as rs
import numpy as np
import cv2
import time
import dwani
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from queue import LifoQueue
import requests
import json
from datetime import datetime

# Set up dwani API configuration
dwani.api_key = os.getenv("DWANI_API_KEY")
dwani.api_base = os.getenv("DWANI_API_BASE_URL")

# Thread pool executor for running blocking tasks
executor = ThreadPoolExecutor(max_workers=3)  # Support up to 3 cameras

# LIFO queue to store frames
frame_queue = LifoQueue(maxsize=6)  # 2 frames per camera for up to 3 cameras

# World state dictionary
world_state = {
    "timestamp": None,
    "camera_serial": None,
    "description": None
}

# JSON Lines file for storing world state (append mode)
WORLD_STATE_FILE = "world_state.jsonl"

# Function to save world state to JSON Lines file (append mode)
def save_world_state():
    try:
        with open(WORLD_STATE_FILE, 'a') as f:
            json.dump(world_state, f)
            f.write('\n')
    except Exception:
        pass  # Silently ignore file write errors

# Synchronous function to describe the image
def _describe_image_sync(image):
    try:
        # Resize image to reduce file size
        resized_image = cv2.resize(image, (320, 240), interpolation=cv2.INTER_AREA)
        temp_file = f"temp_rgb_image_{os.getpid()}_{time.time()}.jpg"
        cv2.imwrite(temp_file, resized_image, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        
        max_retries = 3
        retry_delay = 1
        for attempt in range(max_retries):
            try:
                result = dwani.Vision.caption_direct(
                    file_path=temp_file,
                    query="Provide the list and count of important objects in the image as json format. Do not explain.",
                    model="gemma3",
                    system_prompt="Provide a description of the image."
                )
                return result
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return None
            except Exception:
                if attempt == max_retries - 1:
                    return None
                time.sleep(retry_delay)
            finally:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
    except Exception:
        return None
    return None

# Asynchronous wrapper for describe_image
async def describe_image(image):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, _describe_image_sync, image)
    return result

# Async function to process frames from the queue
async def process_queue():
    global world_state
    while True:
        try:
            frame_data = await asyncio.get_event_loop().run_in_executor(None, frame_queue.get)
            rgb_image, timestamp, camera_serial = frame_data
            print(f"Processing frame from camera {camera_serial} at {timestamp}")  # Debug
            try:
                description = await describe_image(rgb_image.copy())
                if description:
                    world_state["timestamp"] = timestamp
                    world_state["camera_serial"] = camera_serial
                    world_state["description"] = description
                    save_world_state()
                    print(f"Description for camera {camera_serial}: {description}")  # Debug
                else:
                    print(f"No description for camera {camera_serial}")  # Debug
            except Exception:
                pass  # Silently ignore processing errors
            finally:
                frame_queue.task_done()
        except Exception:
            pass  # Silently handle queue errors
        await asyncio.sleep(0)

# Main async function to run the pipeline
async def main():
    # Initialize context to detect all RealSense cameras
    ctx = rs.context()
    devices = ctx.query_devices()
    if not devices:
        print("No RealSense devices detected. Exiting.")
        return

    # Initialize pipelines for available cameras
    pipelines = []
    serial_numbers = []
    last_queue_times = {}
    for device in devices:
        try:
            serial = device.get_info(rs.camera_info.serial_number)
            pipeline = rs.pipeline()
            config = rs.config()
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
            config.enable_device(serial)
            pipeline.start(config)
            pipelines.append(pipeline)
            serial_numbers.append(serial)
            last_queue_times[serial] = time.time()
            print(f"Initialized camera {serial}")
        except Exception:
            continue  # Skip cameras that fail to initialize

    if not pipelines:
        print("No cameras could be initialized. Exiting.")
        return

    print(f"Running with {len(pipelines)} RealSense camera(s).")

    # Start the queue processing task
    queue_task = asyncio.create_task(process_queue())

    description_interval = 3  # seconds

    try:
        while True:
            for pipeline, serial in zip(pipelines, serial_numbers):
                try:
                    # Wait for frames with a timeout
                    frames = pipeline.wait_for_frames(timeout_ms=1000)
                    rgb_frame = frames.get_color_frame()
                    if not rgb_frame:
                        continue

                    rgb_image = np.asanyarray(rgb_frame.get_data())

                    # Add frame to queue every 3 seconds
                    current_time = time.time()
                    if current_time - last_queue_times[serial] >= description_interval:
                        try:
                            timestamp = datetime.now().isoformat()
                            if not frame_queue.full():
                                frame_queue.put_nowait((rgb_image.copy(), timestamp, serial))
                                last_queue_times[serial] = current_time
                                print(f"Queued frame from camera {serial} at {timestamp}")  # Debug
                            else:
                                # Replace oldest frame if queue is full
                                frame_queue.get_nowait()
                                frame_queue.task_done()
                                frame_queue.put_nowait((rgb_image.copy(), timestamp, serial))
                                last_queue_times[serial] = current_time
                                print(f"Replaced frame in queue for camera {serial} at {timestamp}")  # Debug
                        except Exception:
                            pass  # Silently handle queue errors

                    # Display RGB image
                    cv2.imshow(f'RealSense RGB - Camera {serial}', rgb_image)

                except Exception:
                    continue  # Silently skip errors for this camera

            # Check for 'q' key to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            await asyncio.sleep(0)

    finally:
        queue_task.cancel()
        try:
            await queue_task
        except asyncio.CancelledError:
            pass
        for pipeline, serial in zip(pipelines, serial_numbers):
            try:
                pipeline.stop()
            except Exception:
                pass
        cv2.destroyAllWindows()
        executor.shutdown(wait=True)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())