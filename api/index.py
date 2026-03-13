import sys
import os
import traceback
from pathlib import Path

# Modern path resolution for Vercel
sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from app.main import app
except Exception as e:
    # Error Handler for Fast Debugging (Point 8 of Audit)
    print(f"Error importing app.main: {e}")
    traceback.print_exc()
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/{path:path}")
    async def catch_all(path: str):
        return {
            "error": "Failed to load application",
            "message": str(e),
            "traceback": traceback.format_exc(),
            "cwd": os.getcwd()
        }

# Standard exports for Vercel
handler = app
