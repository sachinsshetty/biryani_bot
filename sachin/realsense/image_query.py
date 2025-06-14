import pyrealsense2 as rs
import numpy as np
import cv2
import time
import dwani
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Set up dwani API configuration
dwani.api_key = os.getenv("DWANI_API_KEY")
dwani.api_base = os.getenv("DWANI_API_BASE_URL")

# Thread pool executor for running blocking tasks
executor = ThreadPoolExecutor(max_workers=1)

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

        print(result)
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

# Main async function to run the pipeline
async def main():
    # Configure infrared stream (left IR sensor, Y8 format)
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)  # '1' is the left IR sensor

    pipeline.start(config)

    last_description_time = time.time()
    description_interval = 3  # seconds
    description_task = None

    try:
        while True:
            frames = pipeline.wait_for_frames()
            ir_frame = frames.get_infrared_frame(1)  # Get left IR frame
            if not ir_frame:
                continue

            # Convert to numpy array (already monochrome)
            ir_image = np.asanyarray(ir_frame.get_data())

            # Check if 3 seconds have passed and no description task is running
            current_time = time.time()
            if (current_time - last_description_time >= description_interval and
                    (description_task is None or description_task.done())):
                # Start a new description task
                description_task = asyncio.create_task(describe_image(ir_image.copy()))
                last_description_time = current_time

            # Check if description task is complete
            if description_task and description_task.done():
                try:
                    description = description_task.result()
                    print(f"Image description: {description}")
                except Exception as e:
                    print(f"Error in description: {e}")
                description_task = None

            cv2.imshow('RealSense IR (Monochrome)', ir_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Allow other tasks to run
            await asyncio.sleep(0)

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()
        executor.shutdown(wait=True)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())