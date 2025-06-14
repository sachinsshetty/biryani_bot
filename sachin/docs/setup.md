
Add - daemon.json to /etc/docker/
- sudo systemctl restart docker

sudo docker run --runtime nvidia -it --rm -p 8000:8000 slabstech/dwani-vllm



 vllm serve google/gemma-3-4b-it     --served-model-name gemma3     --host 0.0.0.0     --port 8000     --gpu-memory-utilization 0.9     --tensor-parallel-size 1     --max-model-len 16384     --dtype bfloat16 





export DWANI_API_BASE_URL_VISION=http://127.0.0.1:8000


https://github.com/dwani-ai/docs-indic-server.git

git clone https://github.com/dwani-ai/docs-indic-server.git

cd docs-indic-server
git checkout astra

python3.10 -m venv venv
source venv/bin/activate
pip install -r robot.txt
python src/server/robot_api.py --host 0.0.0.0 --port 7861




https://github.com/dwani-ai/dwani-api-server.git

git clone https://github.com/dwani-ai/dwani-api-server.git

cd dwani-api-server

git checkout astra


python3.10 -m venv venv
source venv/bin/activate


pip install -r requirements.txt
python src/server/robot.py --host 0.0.0.0 --port 8888


<!-- 
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
