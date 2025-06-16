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

# Set environment variable to avoid Qt platform plugin issue
os.environ["QT_QPA_PLATFORM"] = "xcb"  # Use XCB backend for OpenCV on Linux

# Set up dwani API configuration
dwani.api_key = os.getenv("DWANI_API_KEY")
dwani.api_base = os.getenv("DWANI_API_BASE_URL")

# Thread pool executor for running blocking tasks
executor = ThreadPoolExecutor(max_workers=1)

# LIFO queue to store frames
frame_queue = LifoQueue(maxsize=2)

# Synchronous function to detect objects in the image
def _describe_image_sync(image):
    print("Processing image for object detection...")
    # Resize image to reduce file size
    resized_image = cv2.resize(image, (320, 240), interpolation=cv2.INTER_AREA)
    temp_file = "temp_rgb_image.jpg"
    try:
        # Save with moderate JPEG quality
        success = cv2.imwrite(temp_file, resized_image, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not success:
            raise IOError("Failed to write temporary image file")
        
        max_retries = 3
        retry_delay = 1  # seconds
        for attempt in range(max_retries):
            try:
                # Call dwani API with updated prompt
                result = dwani.Vision.caption_direct(
                    file_path=temp_file,
                    query="List all objects in the image with their bounding boxes in the format: [{'label': 'object_name', 'bbox': [x_min, y_min, x_max, y_max]}]. Use pixel coordinates for a 320x240 image. Return only the structured JSON list.",
                    model="gemma3",
                    system_prompt="You are an object detection system. Identify objects in the image and return a JSON list of objects with their bounding boxes in pixel coordinates for a 320x240 image. Output only: [{'label': 'object_name', 'bbox': [x_min, y_min, x_max, y_max]}], with no additional text."
                )
                # Assume result is a dictionary like {'objects': [{'label': 'name', 'bbox': [x_min, y_min, x_max, y_max]}, ...]}
                detections = []
                if isinstance(result, dict) and 'objects' in result:
                    for obj in result['objects']:
                        if 'label' in obj and 'bbox' in obj and len(obj['bbox']) == 4:
                            # Ensure bbox contains integers
                            try:
                                bbox = [int(x) for x in obj['bbox']]
                                detections.append({'label': obj['label'], 'bbox': bbox})
                            except (TypeError, ValueError):
                                print(f"Invalid bounding box format for {obj['label']}")
                else:
                    print("Unexpected API response format")
                return detections
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
        # Ensure file is only deleted if it exists
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                print(f"Error removing temp file: {e}")
    return []  # Return empty list if all retries fail

# Asynchronous wrapper for describe_image
async def describe_image(image):
    loop = asyncio.get_running_loop()
    # Run the synchronous detection function in a thread
    result = await loop.run_in_executor(executor, _describe_image_sync, image)
    return result

# Async function to process frames from the queue
async def process_queue():
    while True:
        # Get the latest frame from the queue
        rgb_image = await asyncio.get_event_loop().run_in_executor(None, frame_queue.get)
        try:
            detections = await describe_image(rgb_image.copy())
            if detections:
                for detection in detections:
                    # Print only object name and bounding box
                    print(f"{detection['label']}: {detection['bbox']}")
            else:
                print("No objects detected.")
        except Exception as e:
            print(f"Error in detection: {e}")
        finally:
            # Mark the task as done
            frame_queue.task_done()
        # Allow other tasks to run
        await asyncio.sleep(0)

# Main async function to run the pipeline
async def main():
    # Configure RGB stream with reduced frame rate
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)  # Reduced to 15 FPS

    try:
        pipeline.start(config)
    except Exception as e:
        print(f"Error starting RealSense pipeline: {e}")
        return

    # Start the queue processing task
    queue_task = asyncio.create_task(process_queue())

    last_queue_time = time.time()
    description_interval = 3  # seconds

    try:
        while True:
            frames = pipeline.wait_for_frames()
            rgb_frame = frames.get_color_frame()
            if not rgb_frame:
                continue

            # Convert to numpy array
            rgb_image = np.asanyarray(rgb_frame.get_data())

            # Add frame to queue every 3 seconds if queue is not full
            current_time = time.time()
            if current_time - last_queue_time >= description_interval:
                if not frame_queue.full():
                    frame_queue.put_nowait(rgb_image.copy())
                    last_queue_time = current_time
                else:
                    # If queue is full, remove the old frame and add the new one
                    try:
                        frame_queue.get_nowait()
                        frame_queue.task_done()
                        frame_queue.put_nowait(rgb_image.copy())
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program terminated by user.")