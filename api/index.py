"""
Vercel Serverless Function entry point for FastAPI backend.
Mounts the main application and serves both static assets and API routes.
"""

import sys
import os

# Insert backend directory to python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
