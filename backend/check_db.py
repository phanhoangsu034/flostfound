import os
import sys

# Add backend directory to sys.path
backend_dir = r"D:\Club\CTV-Team-1X-BET-23-1\backend"
sys.path.append(backend_dir)

from app import create_app
from app.models.user import User

app = create_app('development')
with app.app_context():
    users = User.query.all()
    print(f"Total users: {len(users)}")
    for user in users:
        print(f"User: {user.username}, Email: {user.email}, Avatar URL: '{user.avatar_url}'")
