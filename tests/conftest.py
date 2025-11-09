import os
import sys

# Add the project root directory to Python path
# This allows the tests to import the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Add ComfyUI path to Python path so comfy_api can be imported
COMFYUI_PATH = os.environ.get("COMFYUI_PATH")
if os.path.exists(COMFYUI_PATH):
    sys.path.insert(0, COMFYUI_PATH)
