import sqlite3
import os

def migrate_db(db_path):
    if not os.path.exists(db_path):
        return
    
    print(f"[*] Migrating: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update Item table
        cursor.execute("PRAGMA table_info(item)")
        columns_item = [col[1] for col in cursor.fetchall()]
        
        new_item_columns = [
            ('specific_location', 'VARCHAR(200)'),
            ('category', 'VARCHAR(100)'),
            ('phone_number', 'VARCHAR(20)'),
            ('facebook_url', 'VARCHAR(500)'),
            ('incident_date', 'DATETIME'),
            ('status', 'VARCHAR(20) DEFAULT "Open"'),
            ('image_url', 'VARCHAR(500)')
        ]
        
        for col_name, col_type in new_item_columns:
            if col_name not in columns_item:
                print(f"  [+] Adding {col_name} to item...")
                cursor.execute(f"ALTER TABLE item ADD COLUMN {col_name} {col_type}")
                
        # Update User table
        cursor.execute("PRAGMA table_info(user)")
        columns_user = [col[1] for col in cursor.fetchall()]

        if 'avatar_url' not in columns_user:
            if 'avatar' in columns_user:
                print(f"  [+] Renaming avatar to avatar_url in user...")
                try:
                    cursor.execute("ALTER TABLE user RENAME COLUMN avatar TO avatar_url")
                except:
                    # Fallback for old SQLite
                    cursor.execute("ALTER TABLE user ADD COLUMN avatar_url VARCHAR(300)")
                    cursor.execute("UPDATE user SET avatar_url = avatar")
            else:
                print(f"  [+] Adding avatar_url to user...")
                cursor.execute("ALTER TABLE user ADD COLUMN avatar_url VARCHAR(300)")

        if 'phone_number' not in columns_user:
            if 'phone' in columns_user:
                print(f"  [+] Renaming phone to phone_number in user...")
                try:
                    cursor.execute("ALTER TABLE user RENAME COLUMN phone TO phone_number")
                except:
                    cursor.execute("ALTER TABLE user ADD COLUMN phone_number VARCHAR(20)")
                    cursor.execute("UPDATE user SET phone_number = phone")
            else:
                print(f"  [+] Adding phone_number to user...")
                cursor.execute("ALTER TABLE user ADD COLUMN phone_number VARCHAR(20)")

        if 'about_me' not in columns_user:
             print(f"  [+] Adding about_me to user...")
             cursor.execute("ALTER TABLE user ADD COLUMN about_me TEXT")
                
        conn.commit()
        conn.close()
        print(f"[+] Done with {db_path}\n")
    except Exception as e:
        print(f"  [!] Error migrating {db_path}: {e}")

# Các vị trí database có thể tồn tại (tính từ cả thư mục gốc và thư mục backend)
search_paths = [
    'instance/flostfound_dev.db',
    'instance/flostfound.db',
    'backend/instance/flostfound_dev.db',
    'backend/instance/flostfound.db',
    'flostfound_dev.db',
    'flostfound.db'
]

for path in search_paths:
    migrate_db(path)
