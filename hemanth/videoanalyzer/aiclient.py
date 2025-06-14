import base64
import requests
from config import settings
import dwani

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
    
def call_ai(messages, max_tokens=200):
    url = settings.AI_API_URL
    headers = {"Content-Type": "application/json"}
    data = {
        "model": settings.AI_MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"LM Studio API error: {response.text}")
    return response.json()["choices"][0]["message"]["content"]

def call_dwani_Vision(imagePath, prompt):
    dwani.api_key = settings.DWANI_API_KEY
    dwani.api_base = settings.DWANI_API_URL
    response = dwani.Vision.caption_direct(
        file_path=imagePath,
        query=prompt,
        model=settings.AI_MODEL_NAME
    )
    #print(response)
    return response["answer"]

def call_dwani_chat(prompt):
    dwani.api_key = settings.DWANI_API_KEY
    dwani.api_base = settings.DWANI_API_URL
    response = dwani.Chat(
        query=prompt,
        model=settings.AI_MODEL_NAME
    )
    #print(response)
    return response["answer"]