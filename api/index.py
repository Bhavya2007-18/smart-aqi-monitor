import os
import sys
import traceback
from fastapi import FastAPI

# Add the parent directory to sys.path to ensure 'app' can be found
# On Vercel, the current working directory is usually the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"--- Vercel Diagnostic Log ---")
print(f"CWD: {os.getcwd()}")
print(f"Project Root: {project_root}")
print(f"Python Path: {sys.path}")
print(f"Directory contents: {os.listdir(project_root)}")
print(f"-----------------------------")

try:
    from app.main import app
except ImportError as e:
    print(f"CRITICAL: Import Error in api/index.py: {e}")
    traceback.print_exc()
    app = FastAPI()
    @app.get("/{rest_of_path:path}")
    async def import_error_handler(rest_of_path: str):
        return {
            "error": "FastAPI application could not be loaded",
            "detail": str(e),
            "traceback": traceback.format_exc(),
            "cwd": os.getcwd(),
            "sys_path": sys.path
        }
except Exception as e:
    print(f"CRITICAL: Unexpected Error in api/index.py: {e}")
    traceback.print_exc()
    app = FastAPI()
    @app.get("/{rest_of_path:path}")
    async def general_error_handler(rest_of_path: str):
        return {
            "error": "An unexpected error occurred during bootstrap",
            "detail": str(e),
            "traceback": traceback.format_exc()
        }
