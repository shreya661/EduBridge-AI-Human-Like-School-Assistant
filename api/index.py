"""
Vercel Serverless Function entry point for FastAPI backend.

Vercel requires that 'app' be a top-level module attribute.
We resolve the import path before importing so 'from app.main import app'
always works, regardless of how Vercel sets up /var/task.
"""

import sys
import os

# Build candidate paths in order of preference
_here = os.path.dirname(os.path.abspath(__file__))          # /var/task/api
_root = os.path.dirname(_here)                               # /var/task

_candidates = [
    _here,                                                   # api/ has app/ copied in
    os.path.join(_root, "backend"),                         # root backend/
    _root,                                                   # root itself
    "/var/task/api",                                         # absolute Vercel path for api/
    "/var/task/backend",                                     # absolute Vercel path for backend/
    "/var/task",                                             # absolute Vercel root
]

for _p in _candidates:
    if _p and os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from app.main import app  # noqa: E402 — must be top-level for Vercel
