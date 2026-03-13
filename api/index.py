import sys
import os
from pathlib import Path

# Modern path resolution for Vercel
# Ensure the root directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Proactively print path for potential log inspection
print(f"Loading app from {root_dir}")

from app.main import app

# Vercel requirements
handler = app
