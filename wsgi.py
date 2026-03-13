"""
WSGI entry point for Railway / Gunicorn deployment.
This file lives at the project root so gunicorn can find it easily.
"""
import os
import sys

# ── Fix import path BEFORE any app imports ──────────────────────────────────
# When gunicorn runs from /app (project root), Python's sys.path contains /app.
# This means "from app import ..." would find the ROOT app.py (the old standalone
# file) instead of backend/app/ (the Flask factory package).
# Inserting backend/ at position 0 ensures the correct package is found.
_backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, _backend_dir)

# ── Eventlet monkey-patch (MUST happen before any other imports) ─────────────
import eventlet
eventlet.monkey_patch()

# ── Load .env (no-op on Railway, env vars already injected) ─────────────────
from dotenv import load_dotenv
load_dotenv()

# ── Create Flask application ─────────────────────────────────────────────────
from app import create_app, socketio  # noqa: E402  (backend/app/)

app = create_app()
