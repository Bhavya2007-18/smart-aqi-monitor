import sys
import os
import traceback
import json
from pathlib import Path

# Add project root to sys.path
root_path = str(Path(__file__).resolve().parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

def create_error_response(message, error_detail):
    """Fallback ASGI application to return errors without any dependencies."""
    async def app(scope, receive, send):
        if scope['type'] != 'http':
            return
        
        response_body = json.dumps({
            "error": message,
            "detail": error_detail,
            "traceback": traceback.format_exc(),
            "cwd": os.getcwd(),
            "sys_path": sys.path
        }).encode('utf-8')
        
        await send({
            'type': 'http.response.start',
            'status': 500,
            'headers': [(b'content-type', b'application/json')],
        })
        await send({
            'type': 'http.response.body',
            'body': response_body,
        })
    return app

try:
    # Attempt to load the real application
    from app.main import app as main_app
    app = main_app
except ImportError as e:
    # Specifically handle missing dependency errors (like fastapi not in requirements.txt)
    app = create_error_response("Dependency Error", str(e))
except Exception as e:
    # Handle any other startup crash
    app = create_error_response("Startup Execution Error", str(e))

# For maximum Vercel compatibility
handler = app
