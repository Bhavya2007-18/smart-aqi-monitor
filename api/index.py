import sys
import os
from pathlib import Path

# Fix the path so 'app' can be imported correctly by Vercel's Python builder
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Proactively log path resolution
print(f"Serverless boot from: {root_dir}")

# Import the FastAPI app instance from app/main.py
from app.main import app

# Standard export for Vercel
app = app
