Biryani Bot

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
