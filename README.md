Biryani Bot

Workflow
![biryani-bot-workflow](docs/biryani-bot.drawio.png)

- Credits 
  - Video to Recipe : Hemanth K
  - World Model : Sachin
  - SO101 - caibration + finetuning - Shashank, Utkarsh, Jaybalaji 

- Running the Project
  - Project Setup
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

  - Video to Recipe
    ```bash
    cd video_to_recipe/
    uvicorn main:app
    ```

  - World Model
    ```bash
    cd world_model
    python all_world_v2.py
    ```

---

- Video URL
  - Simple Chicken Biryani for beginners | https://www.youtube.com/watch?v=95BCU1n268w
  - Spicy Spaghetti Pasta Recipe | https://www.youtube.com/watch?v=YXYjwALuA7c


- Robot [actions](docs/action.md)
- Inference [Setup](docs/setup.md)
- Research [Papers](docs/papers.md)
- Reference [Links](docs/links.md)