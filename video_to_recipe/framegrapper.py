import os
import cv2

def extract_frames(video_path, output_folder, interval_sec=10):
    os.makedirs(output_folder, exist_ok=True)
    print(f"Output folder: {output_folder}")
    vidcap = cv2.VideoCapture(video_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    print(f"duration: {duration}")

    count = 0
    sec = 0
    while sec < duration:
        vidcap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        success, image = vidcap.read()
        if not success:
            break
        cv2.imwrite(os.path.join(output_folder, f"frame_{count:03d}.jpg"), image)
        count += 1
        sec += interval_sec
    vidcap.release()