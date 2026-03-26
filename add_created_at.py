import sqlite3
import os

db_path = os.path.join('backend', 'instance', 'flostfound.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        conn.commit()
        print("Successfully added created_at column to user table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name: created_at" in str(e).lower():
            print("Column created_at already exists.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()
else:
    print(f"Database not found at {db_path}")
