import pyrealsense2 as rs
import numpy as np
import cv2

# Configure infrared stream (left IR sensor, Y8 format)
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)  # '1' is the left IR sensor

pipeline.start(config)

try:
    while True:
        frames = pipeline.wait_for_frames()
        ir_frame = frames.get_infrared_frame(1)  # Get left IR frame
        if not ir_frame:
            continue

        # Convert to numpy array (already monochrome)
        ir_image = np.asanyarray(ir_frame.get_data())

        cv2.imshow('RealSense IR (Monochrome)', ir_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    pipeline.stop()
    cv2.destroyAllWindows()
