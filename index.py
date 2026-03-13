import sys
import os
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Proactively print path for potential log inspection
print(f"Loading local app from {root_dir}")

try:
    from app.main import app
except ImportError as e:
    print(f"CRITICAL: Failed to import app.main from {root_dir}")
    print(f"Error: {e}")
    print(f"Current sys.path: {sys.path}")
    raise

# Vercel's Python runtime searches for 'app' or 'handler'
handler = app
