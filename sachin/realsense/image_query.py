import pyrealsense2 as rs
import numpy as np
import cv2
import time
import dwani
import os 

dwani.api_key = os.getenv("DWANI_API_KEY")

dwani.api_base = os.getenv("DWANI_API_BASE_URL")


# External function to describe the image
def describe_image(image):
    # This is a placeholder - implement your image description logic here
    # Could involve computer vision, ML model, or simple image processing
    print("Processing image for description...")

    result = dwani.Vision.caption_direct(
    file_path=image,
    query="Describe this image",
    model="gemma3"
    )
    print(result)

    # Example description (replace with actual implementation)
    return result

# Configure infrared stream (left IR sensor, Y8 format)
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)  # '1' is the left IR sensor

pipeline.start(config)

last_description_time = time.time()
description_interval = 3  # seconds

try:
    while True:
        frames = pipeline.wait_for_frames()
        ir_frame = frames.get_infrared_frame(1)  # Get left IR frame
        if not ir_frame:
            continue

        # Convert to numpy array (already monochrome)
        ir_image = np.asanyarray(ir_frame.get_data())

        # Check if 3 seconds have passed
        current_time = time.time()
        if current_time - last_description_time >= description_interval:
            # Send frame to description function
            description = describe_image(ir_image)
            print(f"Image description: {description}")
            last_description_time = current_time

        cv2.imshow('RealSense IR (Monochrome)', ir_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()