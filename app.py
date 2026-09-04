import sys
import os

# Add the backend directory to the Python path so local imports in main.py work
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# Import the FastAPI app from backend/main.py
from main import app

# Hugging Face Spaces (Gradio SDK) will automatically detect this `app` variable 
# and serve the FastAPI application on port 7860!
