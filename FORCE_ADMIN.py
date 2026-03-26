import sqlite3
from werkzeug.security import generate_password_hash
import os

db_paths = [
    'backend/instance/flostfound.db',
    'backend/instance/flostfound_dev.db',
    'flostfound.db'
]

password_hash = generate_password_hash("123456")

for path in db_paths:
    if os.path.exists(path):
        print(f"FORCING ADMIN INTO {path}...")
        try:
            conn = sqlite3.connect(path)
            c = conn.cursor()
            
            # Check if user table exists
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
            if not c.fetchone():
                print(f"  Table 'user' not found in {path}. Skipping.")
                continue

            # Delete any existing 'admin' to avoid conflicts
            c.execute("DELETE FROM user WHERE username='admin'")
            
            # Insert fresh admin
            c.execute("""
                INSERT INTO user (username, email, password_hash, is_admin, is_banned, trust_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("admin", "admin@fpt.edu.vn", password_hash, 1, 0, 100))
            
            conn.commit()
            conn.close()
            print(f"  Admin 'admin' successfully injected into {path}.")
        except Exception as e:
            print(f"  Failed {path}: {e}")

print("\n--- ALL DONE ---")
