import dwani
import os

dwani.api_key = os.getenv("DWANI_API_KEY")

dwani.api_base = os.getenv("DWANI_API_BASE_URL")


result = dwani.Vision.caption_direct(
    file_path="image.png",
    query="Describe this logo",
    model="gemma3"
)
print(result)

