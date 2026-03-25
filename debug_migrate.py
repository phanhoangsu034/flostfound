import sqlite3
import os

db_path = r'C:\Users\dell 5411\Desktop\JS-CLUB\LÀM PROJECT\CTV-Team-1X-BET-23-1\backend\instance\flostfound.db'
with open('debug_migration.txt', 'w') as f:
    if os.path.exists(db_path):
        f.write(f"DB exists: {db_path}\n")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
            f.write("SUCCESS: Added created_at column.\n")
        except Exception as e:
            f.write(f"ERROR: {e}\n")
            if "duplicate column" in str(e).lower():
                f.write("Column already exists.\n")
        finally:
            conn.close()
    else:
        f.write(f"DB NOT FOUND at: {db_path}\n")
