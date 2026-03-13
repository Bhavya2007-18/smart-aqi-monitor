import os
import sys
import traceback

# Ensure project root is in path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.insert(0, path)

try:
    from app.main import app
except Exception as e:
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

# For maximum Vercel compatibility, export as both 'app' and 'handler'
app = app
handler = app
