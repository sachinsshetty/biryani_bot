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
    interval_sec: Optional[int] = 1
    batch_size: Optional[int] = 10
    max_new_tokens: Optional[int] = 200

def save_to_file(filename, data):
    with open(filename, 'w') as f:
        f.write(data)

@app.post("/analyzeVideoLocal")
def analyze_video_local(request: VideoAnalysisRequest):
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

@app.post("/analyzeVideo")
def analyze_video_cloud(request: VideoAnalysisRequest):
    session_id = str(uuid.uuid4())
    #workdir = f"tmp_{session_id}"
    #replace with env
    workdir = Path(settings.VIDEO_INPUT_PATH).joinpath(session_id)
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
        for i in range(0, len(frame_paths)):
            print(f"image path:{frame_paths[i]}")
            user_content = []
            user_content.append({
                "type": "text",
                "text": "Describe the main events and actions observed in this video segment, then outline a corresponding action policy for the Lerobot"
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
            summary = aiclient.call_dwani_Vision(frame_paths[i], messages)
            #print(f"messages: {summary}")
            summaries.append(summary)

        full_summary = "\n".join(summaries)
        print(f"full_summary = {full_summary}")
        sf_path = os.path.join(workdir, "summary.txt")
        save_to_file(sf_path,full_summary)
        #convert whole summaries to vla input
        prompt = f"Summarize the following context as concisely as possible, capturing only the essential information and main points. Remove all unnecessary details, examples, or subplots. Present the summary in a format suitable for smolvla input—extremely brief, focused, and clear. Context:[{full_summary}]"
        action_tasks = aiclient.call_dwani_chat(prompt)
        print(f"action_tasks = {action_tasks}")
        at_path = os.path.join(workdir, "summary.txt")
        save_to_file(at_path,action_tasks)
        return {"Summary": full_summary, "Action Task": action_tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    #finally:
        #shutil.rmtree(workdir, ignore_errors=True)