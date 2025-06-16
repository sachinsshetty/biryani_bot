Inference Setup

- GPU Server 
  - Add - daemon.json to /etc/docker/
  - sudo systemctl restart docker

- Start VLLm container
  - sudo docker run --runtime nvidia -it --rm -p 8000:8000 slabstech/dwani-vllm

- vllm serve google/gemma-3-4b-it \
  --served-model-name gemma3 \
  --host 0.0.0.0 \
  --port 8000 \
  --gpu-memory-utilization 0.85 \
  --tensor-parallel-size 1 \
  --max-model-len 8192 \
  --dtype bfloat16 \
  --max-num-batched-tokens 4096 \
  --enable-chunked-prefill \
  --max-num-seq 32 \
  --enforce-eager 

vllm serve Qwen/Qwen2.5-VL-7B-Instruct \
    --served-model-name qwen2.5-vl \
    --host 0.0.0.0 \
    --port 8000 \
    --gpu-memory-utilization 0.9 \
    --tensor-parallel-size 1 \
    --max-model-len 16384 \
    --dtype bfloat16 \
    --trust-remote-code



https://github.com/dwani-ai/docs-indic-server.git

git clone https://github.com/dwani-ai/docs-indic-server.git

cd docs-indic-server
git checkout astra

python3.10 -m venv venv
source venv/bin/activate
pip install -r robot.txt
python src/server/robot_api.py --host 0.0.0.0 --port 7861



export DWANI_API_BASE_URL_VISION=http://127.0.0.1:7861

export DWANI_API_BASE_URL_LLM=http://127.0.0.1:7861

https://github.com/dwani-ai/dwani-api-server.git

git clone https://github.com/dwani-ai/dwani-api-server.git

cd dwani-api-server

git checkout astra


python3.10 -m venv venv
source venv/bin/activate


pip install -r requirements.txt
python src/server/robot.py --host 0.0.0.0 --port 




 
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



<!-- 

  - vllm serve google/gemma-3-4b-it     --served-model-name gemma3     --host 0.0.0.0     --port 8000     --gpu-memory-utilization 0.9     --tensor-parallel-size 1     --max-model-len 16384     --dtype bfloat16 

 ./build/bin/llama-server   --model hf_models/gemma-3-27b-it-q4_0.gguf  --mmproj hf_models/mmproj-model-f16-27B.gguf  --host 0.0.0.0   --port 7890   --n-gpu-layers 100   --threads 4   --ctx-size 4096   --batch-size 256


 ./build/bin/llama-server   --model hf_models/gemma-3-27b-it-q4_0.gguf  --mmproj hf_models/mmproj-model-f16-27B.gguf  --host 0.0.0.0   --port 7891   --n-gpu-layers 100   --threads 4   --ctx-size 4096   --batch-size 256


 ./build/bin/llama-server   --model hf_models/gemma-3-27b-it-q4_0.gguf  --mmproj hf_models/mmproj-model-f16-27B.gguf  --host 0.0.0.0   --port 7892   --n-gpu-layers 100   --threads 4   --ctx-size 4096   --batch-size 256



export DWANI_API_BASE_URL_VISION=http://127.0.0.1:7891


python src/server/robot_api.py --host 0.0.0.0 --port 7861



python src/server/robot.py --host 0.0.0.0 --port 8888


export DWANI_API_BASE_URL_VISION=http://127.0.0.1:7891

python src/server/robot_api.py --host 0.0.0.0 --port 7862


python src/server/robot.py --host 0.0.0.0 --port 8889


export DWANI_API_BASE_URL_VISION=http://127.0.0.1:7892

python src/server/robot_api.py --host 0.0.0.0 --port 7863


python src/server/robot.py --host 0.0.0.0 --port 8890

-->
