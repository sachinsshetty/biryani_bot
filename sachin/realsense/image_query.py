import pyrealsense2 as rs
import numpy as np
import cv2
import time
import dwani
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from queue import LifoQueue

# Set up dwani API configuration
dwani.api_key = os.getenv("DWANI_API_KEY")
dwani.api_base = os.getenv("DWANI_API_BASE_URL")

# Thread pool executor for running blocking tasks
executor = ThreadPoolExecutor(max_workers=1)

# LIFO queue to store frames
frame_queue = LifoQueue(maxsize=1)  # Limit to 1 to keep only the latest frame

# Synchronous function to describe the image (to be run in a thread)
def _describe_image_sync(image):
    print("Processing image for description...")
    temp_file = "temp_ir_image.jpg"
    cv2.imwrite(temp_file, image)
    
    try:
        result = dwani.Vision.caption_direct(
            file_path=temp_file,
            query="Describe the infrared image",
            model="gemma3",
            system_prompt="Provide a detailed description of the infrared image."
        )
        return result
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

# Asynchronous wrapper for describe_image
async def describe_image(image):
    loop = asyncio.get_running_loop()
    # Run the synchronous description function in a thread
    result = await loop.run_in_executor(executor, _describe_image_sync, image)
    return result

# Async function to process frames from the queue
async def process_queue():
    while True:
        # Get the latest frame from the queue (blocks until a frame is available)
        ir_image = await asyncio.get_event_loop().run_in_executor(None, frame_queue.get)
        try:
            description = await describe_image(ir_image.copy())
            print(f"Image description: {description}")
        except Exception as e:
            print(f"Error in description: {e}")
        finally:
            # Mark the task as done to allow the queue to accept new frames
            frame_queue.task_done()
        # Allow other tasks to run
        await asyncio.sleep(0)

# Main async function to run the pipeline
async def main():
    # Configure infrared stream (left IR sensor, Y8 format)
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)  # '1' is the left IR sensor

    pipeline.start(config)

    # Start the queue processing task
    queue_task = asyncio.create_task(process_queue())

    last_queue_time = time.time()
    description_interval = 3  # seconds

    try:
        while True:
            frames = pipeline.wait_for_frames()
            ir_frame = frames.get_infrared_frame(1)  # Get left IR frame
            if not ir_frame:
                continue

            # Convert to numpy array (already monochrome)
            ir_image = np.asanyarray(ir_frame.get_data())

            # Add frame to queue every 3 seconds if queue is not full
            current_time = time.time()
            if current_time - last_queue_time >= description_interval:
                if not frame_queue.full():
                    frame_queue.put_nowait(ir_image.copy())  # Add latest frame to queue
                    last_queue_time = current_time
                else:
                    # If queue is full, remove the old frame and add the new one
                    try:
                        frame_queue.get_nowait()
                        frame_queue.task_done()
                        frame_queue.put_nowait(ir_image.copy())
                        last_queue_time = current_time
                    except:
                        pass  # Queue might be empty due to concurrent access

            cv2.imshow('RealSense IR (Monochrome)', ir_image)
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