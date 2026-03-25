import sqlite3
import os
import sys

# Try multiple possible paths to be 100% sure
paths = [
    r"C:\Users\dell 5411\Desktop\JS-CLUB\LÀM PROJECT\CTV-Team-1X-BET-23-1\backend\instance\flostfound.db",
    r"C:\Users\dell 5411\Desktop\JS-CLUB\LÀM PROJECT\CTV-Team-1X-BET-23-1\instance\flostfound.db",
    os.path.join(os.getcwd(), 'backend', 'instance', 'flostfound.db'),
    os.path.join(os.getcwd(), 'instance', 'flostfound.db')
]

for db_path in paths:
    if os.path.exists(db_path):
        print(f"Target found: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
            print(f"SUCCESS: Added column to {db_path}")
        except sqlite3.OperationalError as e:
            print(f"INFO: {e}")
        finally:
            conn.close()
    else:
        print(f"Not found: {db_path}")
