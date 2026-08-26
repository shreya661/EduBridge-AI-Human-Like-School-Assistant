"""
Vercel Serverless Function entry point for FastAPI backend.
Resolves path correctly whether backend/ is at the root or in api/ subdirectory.
"""

import sys
import os

# Current directory is /var/task/api on Vercel (where api/ lives)
# Try multiple resolution strategies
_cur = os.path.dirname(os.path.abspath(__file__))  # api/
_root = os.path.dirname(_cur)                        # project root

# Strategy 1: api/app exists (copied bundle)
_api_app = os.path.join(_cur, "app")
# Strategy 2: backend/app exists at root
_backend = os.path.join(_root, "backend")

for path in [_cur, _backend, _root]:
    if path and path not in sys.path and os.path.isdir(path):
        sys.path.insert(0, path)

try:
    from app.main import app
except ModuleNotFoundError:
    try:
        from backend.app.main import app
    except ModuleNotFoundError:
        # Last resort: absolute Vercel path
        vercel_backend = "/var/task/backend"
        if vercel_backend not in sys.path:
            sys.path.insert(0, vercel_backend)
        from app.main import app
