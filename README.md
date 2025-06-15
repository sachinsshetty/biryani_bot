Biryani 

- [Inference Setup](sachin/docs/setup.md)

- World State
  - cd sachin/realsense
  - python world_state.py

- Simple Inference

export DWANI_API_KEY='your_api_key_here'

export DWANI_API_BASE_URL='https://dwani-biryani.hf.space'

git clone https://github.com/sachinsshetty/biryani_bot

cd sachin/server

python vlm.py

or 
```python
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
```


----




- Robot [actions](action.md)

- Papers
  - RTC - https://github.com/Physical-Intelligence/real-time-chunking-kinetix
  - OpenVLA - https://openvla.github.io/
    - https://huggingface.co/openvla
    - https://arxiv.org/abs/2406.09246
  - smolVLA
    - https://learnopencv.com/smolvla-lerobot-vision-language-action-model/
    - https://arxiv.org/abs/2506.01844

- SO-101 - Assemby and setup
  - Video : https://www.youtube.com/watch?v=70GuJf2jbYk
  - https://huggingface.co/docs/lerobot/so101
  - https://github.com/huggingface/lerobot/blob/main/examples/12_use_so101.md


- HF - leRobot - https://www.youtube.com/watch?v=L0uxfZMlkag



- Items
 - Intel RealSense D405 depth cameras
   - https://dev.intelrealsense.com/docs/compiling-librealsense-for-linux-ubuntu-guide
   - https://dev.intelrealsense.com/docs/opencv-wrapper
   - Jetson - https://dev.intelrealsense.com/docs/nvidia-jetson-tx2-installation
   - Rpi 3 - https://dev.intelrealsense.com/docs/using-depth-camera-with-raspberry-pi-3
   - python - https://github.com/IntelRealSense/librealsense/blob/master/wrappers/python/examples/python-tutorial-1-depth.py

​ - NVIDIA Jetson Orin Nano Developer Kits
  -https://www.nvidia.com/en-gb/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/

- Automatica - Munich
  - https://automatica-munich.com/en/trade-fair/tickets/