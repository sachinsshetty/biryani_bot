Biryani Bot


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

https://github.com/dwani-ai/docs-indic-server.git
cd docs-indic-server
git checkout astra

pip install -r robot.txt
python src/server/robot_api.py --host 0.0.0.0 --port 7861


<!-- 

sudo docker run --gpus all -it --rm nvcr.io/nvidia/tritonserver:25.01-vllm-python-py3


nvcr.io/nvidia/tritonserver:25.01-vllm-python-py3


nvcr.io/nvidia/tritonserver:25.04-vllm-python-py3


 vllm serve google/gemma-3-4b-it     --served-model-name gemma3     --host 0.0.0.0     --port 7890     --gpu-memory-utilization 0.9     --tensor-parallel-size 1     --max-model-len 16384     --dtype bfloat16 



Add - daemon.json to /etc/docker/
- sudo systemctl restart docker

sudo docker run --runtime nvidia -it --rm -p 7890:8000 slabstech/dwani-vllm


export HF_TOKEN='hsdfsdfsdf'


export API_KEY_SECRET="dwani-mobile-app"
export CHAT_RATE_LIMIT="100/minute"
export DWANI_API_BASE_URL_PDF="http://127.0.0.1:7861"
export DWANI_API_BASE_URL_VISION="http://127.0.0.1:7861"
export DWANI_API_BASE_URL_LLM="http://127.0.0.1:7861"
export SPEECH_RATE_LIMIT="5/minute"
export ENCRYPTION_KEY="tete"
export DEFAULT_ADMIN_USER="admin"
export DEFAULT_ADMIN_PASSWORD="dwani-987-123"


sudo apt-get update
sudo apt-get install ninja-build

sudo apt-get install libcurl4-openssl-dev

sudo apt-get install -y build-essential python3-dev python3-setuptools make cmake
sudo apt-get install -y ffmpeg libavcodec-dev libavfilter-dev libavformat-dev libavutil-dev
sudo apt install -y poppler-utils
mkdir dwani_org
cd dwani_org


git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp

cmake -B build -DGGML_CUDA=ON

cmake --build build --config Release -j2

python -m venv --system-site-packages venv
source venv/bin/activate
pip install huggingface_hub
mkdir hf_models 

huggingface-cli download google/gemma-3-27b-it-qat-q4_0-gguf --local-dir hf_models/



 ./build/bin/llama-server   --model hf_models/gemma-3-27b-it-q4_0.gguf  --mmproj hf_models/mmproj-model-f16-27B.gguf  --host 0.0.0.0   --port 7890   --n-gpu-layers 100   --threads 4   --ctx-size 4096   --batch-size 256

 -->