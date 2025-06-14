import os
import shutil
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import aiclient
import videodownloader
import framegrapper
from config import settings
from pathlib import Path


app = FastAPI(title="Video Analyzer")

class VideoAnalysisRequest(BaseModel):
    youtube_url: str = "https://www.youtube.com/watch?v=95BCU1n268w"
    interval_sec: Optional[int] = 20
    batch_size: Optional[int] = 2
    max_new_tokens: Optional[int] = 200

@app.post("/analyze")
def analyze_video(request: VideoAnalysisRequest):
    session_id = str(uuid.uuid4())
    #workdir = f"tmp_{session_id}"
    #replace with env
    workdir = Path(settings.VIDEO_INPUT_PATH)
    os.makedirs(workdir, exist_ok=True)
    video_path = os.path.join(workdir, "video.mp4")
    frames_dir = os.path.join(workdir, "frames")

    try:
        videodownloader.download_video(request.youtube_url, video_path) 
        print(f"Downloaded: {video_path}")

        #frame grapper from video
        framegrapper.extract_frames(video_path, frames_dir, interval_sec=request.interval_sec)
        frame_paths = sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith('.jpg')])
        if not frame_paths:
            raise HTTPException(status_code=400, detail="No frames extracted from video.")

        summaries = []
        for i in range(0, len(frame_paths), request.batch_size):
            if i == 2:
                break
            batch = frame_paths[i:i+request.batch_size]
            user_content = []
            for f in batch:
                img_b64 = aiclient.encode_image_to_base64(f)
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                })
            user_content.append({
                "type": "text",
                "text": "Describe the main events and actions observed in this video segment, "
                "then outline a corresponding action policy for the Lerobot framework that enables a robot to replicate these actions for completing recipe."
                #"text": "Describe the key events and actions in this segment of the video."
            })
            messages = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": "You are a helpful assistant."}]
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ]
            #print(f"messages: {messages}")
            summary = aiclient.call_ai(messages, max_tokens=request.max_new_tokens)
            print(f"messages: {summary}")
            summaries.append(summary)

        full_summary = "\n".join(summaries)
        return {"summary": full_summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    #finally:
        #shutil.rmtree(workdir, ignore_errors=True)
