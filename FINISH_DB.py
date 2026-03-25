import sqlite3
import os

# Every DB likely to be used
db_paths = [
    'backend/instance/flostfound_dev.db',
    'backend/instance/flostfound.db',
    'instance/flostfound.db',
    'backend/flostfound.db',
    'flostfound.db'
]

def migrate(path):
    if not os.path.exists(path):
        return
    print(f"MIGRATING {path}...")
    try:
        conn = sqlite3.connect(path)
        c = conn.cursor()
        
        # User table
        try: c.execute("ALTER TABLE user ADD COLUMN is_banned BOOLEAN DEFAULT 0")
        except: pass
        try: c.execute("ALTER TABLE user ADD COLUMN level INTEGER DEFAULT 3")
        except: pass
        try: c.execute("ALTER TABLE user ADD COLUMN ban_until DATETIME")
        except: pass
        try: c.execute("ALTER TABLE user ADD COLUMN trust_score INTEGER DEFAULT 100")
        except: pass
        try: c.execute("ALTER TABLE user ADD COLUMN last_seen DATETIME")
        except: pass
        
        # Item table
        try: c.execute("ALTER TABLE item ADD COLUMN status VARCHAR(20) DEFAULT 'Open'")
        except: pass

        conn.commit()
        conn.close()
        print(f"  Done {path}")
    except Exception as e:
        print(f"  Error {path}: {e}")

for p in db_paths:
    migrate(p)

print("\nDATABASE MIGRATION FINISHED!")
