"""
Application entry point for F-LostFound
"""
import os
import sys

# Fix import path: ensure 'backend/' is in sys.path so that
# 'from app import ...' finds backend/app/ instead of the root app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app, socketio
from app.extensions import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, use_reloader=True, log_output=True)
