Biryani Bot

- Running the Robot
  ```bash
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```
- Video to Recipe
  ```bash
  cd hemanth/
  uvicorn main:app
  ```

- World State
  ```bash
  cd sachin/realsense
  python world_state.py
  ```

---

- Robot [actions](docs/action.md)
- Inference [Setup](docs/setup.md)
- Research [Papers](docs/papers.md)
- Reference [Links](docs/links.md)