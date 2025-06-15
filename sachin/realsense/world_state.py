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
import paho.mqtt.client as mqtt
import json
import datetime
from threading import Lock

# Set up dwani API configuration
dwani.api_key = os.getenv("DWANI_API_KEY")
dwani.api_base = os.getenv("DWANI_API_BASE_URL")

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_TIMESTAMP = "realsense/image/timestamp"
MQTT_TOPIC_DESCRIPTION = "realsense/image/description"
MQTT_CLIENT_ID = "realsense_client"

# Global System State
class SystemState:
    def __init__(self):
        self.lock = Lock()
        self.last_timestamp = None
        self.last_description = None
        self.frame_count = 0
        self.successful_descriptions = 0
        self.failed_descriptions = 0
        self.last_state_change = None

    def update_timestamp(self, timestamp):
        with self.lock:
            self.last_timestamp = timestamp
            self.frame_count += 1
            self.last_state_change = datetime.datetime.now().isoformat()
            return self.get_state()

    def update_description(self, description, success=True):
        with self.lock:
            self.last_description = description
            if success:
                self.successful_descriptions += 1
            else:
                self.failed_descriptions += 1
            self.last_state_change = datetime.datetime.now().isoformat()
            return self.get_state()

    def get_state(self):
        with self.lock:
            return {
                "last_timestamp": self.last_timestamp,
                "last_description": self.last_description,
                "frame_count": self.frame_count,
                "successful_descriptions": self.successful_descriptions,
                "failed_descriptions": self.failed_descriptions,
                "last_state_change": self.last_state_change
            }

# Initialize system state
system_state = SystemState()

# MQTT Client Setup
mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID)
mqtt_connected = False

def on_connect(client, userdata, flags, rc, properties=None):
    global mqtt_connected
    if rc == 0:
        print("Connected to MQTT broker")
        mqtt_connected = True
    else:
        print(f"Failed to connect to MQTT broker with code {rc}")

def on_disconnect(client, userdata, rc, properties=None):
    global mqtt_connected
    mqtt_connected = False
    print("Disconnected from MQTT broker")

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

# Connect to MQTT broker
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    mqtt_client.loop_start()
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")

# Thread pool executor for running blocking tasks
executor = ThreadPoolExecutor(max_workers=1)

# LIFO queue to store frames and timestamps
frame_queue = LifoQueue(maxsize=2)

# Synchronous function to describe the image
def _describe_image_sync(image):
    print("Processing image for description...")
    resized_image = cv2.resize(image, (320, 240), interpolation=cv2.INTER_AREA)
    temp_file = "temp_rgb_image.jpg"
    cv2.imwrite(temp_file, resized_image, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    
    max_retries = 3
    retry_delay = 1
    for attempt in range(max_retries):
        try:
            result = dwani.Vision.caption_direct(
                file_path=temp_file,
                query="Describe the image",
                model="gemma3",
                system_prompt="Provide a description of the image."
            )
            return result
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Rate limit hit, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
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
    return None

# Asynchronous wrapper for describe_image
async def describe_image(image):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, _describe_image_sync, image)
    return result

# Async function to process frames from the queue
async def process_queue():
    while True:
        # Get the latest frame and timestamp
        rgb_image, capture_timestamp = await asyncio.get_event_loop().run_in_executor(None, frame_queue.get)
        try:
            description = await describe_image(rgb_image.copy())
            state = system_state.update_description(description, success=bool(description))
            if description:
                print(f"Image description: {description}")
                if mqtt_connected:
                    payload = {
                        "timestamp": capture_timestamp,
                        "description": description,
                        "system_state": state
                    }
                    mqtt_client.publish(MQTT_TOPIC_DESCRIPTION, json.dumps(payload), qos=1)
            else:
                print("Failed to get description after retries.")
                if mqtt_connected:
                    payload = {
                        "timestamp": capture_timestamp,
                        "description": None,
                        "system_state": state
                    }
                    mqtt_client.publish(MQTT_TOPIC_DESCRIPTION, json.dumps(payload), qos=1)
        except Exception as e:
            print(f"Error in description: {e}")
            state = system_state.update_description(None, success=False)
            if mqtt_connected:
                payload = {
                    "timestamp": capture_timestamp,
                    "description": str(e),
                    "system_state": state
                }
                mqtt_client.publish(MQTT_TOPIC_DESCRIPTION, json.dumps(payload), qos=1)
        finally:
            frame_queue.task_done()
        await asyncio.sleep(0)

# Main async function
async def main():
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)

    pipeline.start(config)
    queue_task = asyncio.create_task(process_queue())

    last_queue_time = time.time()
    description_interval = 3

    try:
        while True:
            frames = pipeline.wait_for_frames()
            rgb_frame = frames.get_color_frame()
            if not rgb_frame:
                continue

            rgb_image = np.asanyarray(rgb_frame.get_data())

            current_time = time.time()
            if current_time - last_queue_time >= description_interval:
                capture_timestamp = datetime.datetime.now().isoformat()
                state = system_state.update_timestamp(capture_timestamp)
                if not frame_queue.full():
                    frame_queue.put_nowait((rgb_image.copy(), capture_timestamp))
                    last_queue_time = current_time
                    if mqtt_connected:
                        payload = {
                            "timestamp": capture_timestamp,
                            "system_state": state
                        }
                        mqtt_client.publish(MQTT_TOPIC_TIMESTAMP, json.dumps(payload), qos=1)
                else:
                    try:
                        frame_queue.get_nowait()
                        frame_queue.task_done()
                        frame_queue.put_nowait((rgb_image.copy(), capture_timestamp))
                        last_queue_time = current_time
                        if mqtt_connected:
                            payload = {
                                "timestamp": capture_timestamp,
                                "system_state": state
                            }
                            mqtt_client.publish(MQTT_TOPIC_TIMESTAMP, json.dumps(payload), qos=1)
                    except:
                        pass

            cv2.imshow('RealSense RGB', rgb_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            await asyncio.sleep(0)

    finally:
        queue_task.cancel()
        try:
            await queue_task
        except asyncio.CancelledError:
            pass
        pipeline.stop()
        cv2.destroyAllWindows()
        executor.shutdown(wait=True)
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())