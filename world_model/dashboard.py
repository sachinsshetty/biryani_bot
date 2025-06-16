import gradio as gr
import pandas as pd
import json
import time
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# File to monitor
JSONL_FILE = "world_state.jsonl"

# Function to read and parse the latest state from the JSONL file
def read_latest_state():
    try:
        # Read the last line of the JSONL file
        with open(JSONL_FILE, 'r') as f:
            lines = f.readlines()
            if not lines:
                return "No data available in the file."
            
            # Parse the last line
            last_line = lines[-1].strip()
            data = json.loads(last_line)
            
            # Extract the objects from the description field
            description = json.loads(data['description']['answer'])
            objects = description['objects']
            
            # Convert to a pandas DataFrame for display
            df = pd.DataFrame(objects)
            return df
    except Exception as e:
        return f"Error reading file: {str(e)}"

# Function to check for file updates
def check_file_updates():
    global last_modified
    try:
        current_modified = os.path.getmtime(JSONL_FILE)
        if 'last_modified' not in globals() or current_modified > last_modified:
            last_modified = current_modified
            return read_latest_state()
        return None  # No update
    except Exception as e:
        return f"Error checking file: {str(e)}"

# File system event handler for continuous monitoring
class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('world_state.jsonl'):
            return check_file_updates()

# Function to start the file watcher
def start_file_watcher():
    observer = Observer()
    event_handler = FileChangeHandler()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    return observer

# Gradio interface function
def display_system_state():
    state = read_latest_state()
    return state

# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# System State Monitor")
    gr.Markdown("Displays the latest state of objects from the `world_state.jsonl` file.")
    
    # Output component to display the state
    output = gr.DataFrame(label="Current System State")
    
    # Button to manually refresh
    refresh_btn = gr.Button("Refresh")
    
    try:
        # Try using demo.load with every parameter
        demo.load(fn=display_system_state, outputs=output, every=5)
    except TypeError as e:
        print(f"Error using demo.load with every: {str(e)}. Falling back to threading-based polling.")
        # Fallback to threading-based polling
        def periodic_update():
            while True:
                state = check_file_updates()
                if state is not None:
                    output.value = state  # Update the DataFrame value
                time.sleep(5)
        threading.Thread(target=periodic_update, daemon=True).start()

    # Bind the refresh button
    refresh_btn.click(fn=display_system_state, outputs=output)

# Start the file watcher
observer = start_file_watcher()

# Launch the Gradio app
try:
    demo.launch()
finally:
    # Stop the observer when the app is closed
    observer.stop()
    observer.join()