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
executor = ThreadPoolExecutor(max_workers=1)

# LIFO queue to store frames (increased to 2 for slight buffering)
frame_queue = LifoQueue(maxsize=2)

# World state dictionary
world_state = {
    "timestamp": None,
    "description": None
}

# JSON Lines file for storing world state (append mode)
WORLD_STATE_FILE = "world_state.jsonl"

# Function to save world state to JSON Lines file (append mode)
def save_world_state():
    try:
        with open(WORLD_STATE_FILE, 'a') as f:
            json.dump(world_state, f)
            f.write('\n')  # Add newline to separate JSON objects
        print(f"World state appended to {WORLD_STATE_FILE}")
    except Exception as e:
        print(f"Error saving world state: {e}")

# Synchronous function to describe the image (to be run in a thread)
def _describe_image_sync(image):
    print("Processing image for description...")
    # Resize image to reduce file size
    resized_image = cv2.resize(image, (320, 240), interpolation=cv2.INTER_AREA)
    temp_file = "temp_rgb_image.jpg"
    # Save with moderate JPEG quality
    cv2.imwrite(temp_file, resized_image, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    
    max_retries = 3
    retry_delay = 1  # seconds
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
            if e.response.status_code == 429:  # Rate limit
                print(f"Rate limit hit, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise e
        except Exception as e:
            print(f"Error in API call: {e}")
            if attempt == max_retries - 1:
                raise e
            time.sleep(retry_delay)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    return None  # Return None if all retries fail

# Asynchronous wrapper for describe_image
async def describe_image(image):
    loop = asyncio.get_running_loop()
    # Run the synchronous description function in a thread
    result = await loop.run_in_executor(executor, _describe_image_sync, image)
    return result

# Async function to process frames from the queue
async def process_queue():
    global world_state
    while True:
        # Get the latest frame from the queue (blocks until a frame is available)
        frame_data = await asyncio.get_event_loop().run_in_executor(None, frame_queue.get)
        rgb_image, timestamp = frame_data  # Unpack image and timestamp
        try:
            description = await describe_image(rgb_image.copy())
            if description:
                print(f"Image description: {description}")
                # Update world state
                world_state["timestamp"] = timestamp
                world_state["description"] = description
                save_world_state()
            else:
                print("Failed to get description after retries.")
        except Exception as e:
            print(f"Error in description: {e}")
        finally:
            # Mark the task as done to allow the queue to accept new frames
            frame_queue.task_done()
        # Allow other tasks to run
        await asyncio.sleep(0)

# Main async function to run the pipeline
async def main():
    # Configure RGB stream with reduced frame rate
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)  # Reduced to 15 FPS

    pipeline.start(config)

    # Start the queue processing task
    queue_task = asyncio.create_task(process_queue())

    last_queue_time = time.time()
    description_interval = 3  # seconds

    try:
        while True:
            frames = pipeline.wait_for_frames()
            rgb_frame = frames.get_color_frame()  # Get RGB frame
            if not rgb_frame:
                continue

            # Convert to numpy array (already in BGR format for OpenCV)
            rgb_image = np.asanyarray(rgb_frame.get_data())

            # Add frame to queue every 3 seconds if queue is not full
            current_time = time.time()
            if current_time - last_queue_time >= description_interval:
                if not frame_queue.full():
                    # Store image and timestamp in queue
                    timestamp = datetime.now().isoformat()
                    frame_queue.put_nowait((rgb_image.copy(), timestamp))
                    last_queue_time = current_time
                else:
                    # If queue is full, remove the old frame and add the new one
                    try:
                        frame_queue.get_nowait()
                        frame_queue.task_done()
                        timestamp = datetime.now().isoformat()
                        frame_queue.put_nowait((rgb_image.copy(), timestamp))
                        last_queue_time = current_time
                    except:
                        pass  # Queue might be empty due to concurrent access

            cv2.imshow('RealSense RGB', rgb_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Allow other tasks to run
            await asyncio.sleep(0)

    finally:
        # Cancel the queue processing task
        queue_task.cancel()
        try:
            await queue_task
        except asyncio.CancelledError:
            pass
        pipeline.stop()
        cv2.destroyAllWindows()
        executor.shutdown(wait=True)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())