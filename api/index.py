"""
Vercel Serverless Function entry point for FastAPI backend.

On Vercel, this file lives at /var/task/api/index.py
The app/ package lives at /var/task/api/app/
We insert /var/task/api into sys.path so `from app.main import app` resolves correctly.
"""

import sys
import os

# /var/task/api  — the directory containing this file and the app/ package
_here = os.path.dirname(os.path.abspath(__file__))

# Ensure this directory is first on the path
if _here not in sys.path:
    sys.path.insert(0, _here)

from app.main import app  # noqa: E402 — must be top-level for Vercel
