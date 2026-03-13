import sys
import os
from pathlib import Path

# Modern path resolution for Vercel
# Ensure the root directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# Proactively print path for potential log inspection
print(f"Loading app from {root_dir}")

from app.main import app

# Vercel's Python runtime searches for 'app' or 'handler'
handler = app
