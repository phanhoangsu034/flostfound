import sys
import os
from sqlalchemy import text

# Set current path for imports
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    print(f"Current Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Check 'user' table
    try:
        # Add columns to user table
        db.session.execute(text("ALTER TABLE user ADD COLUMN is_banned BOOLEAN DEFAULT 0"))
        print("Added is_banned to 'user'")
    except Exception as e:
        print(f"is_banned may already exist or error: {e}")
        
    try:
        db.session.execute(text("ALTER TABLE user ADD COLUMN ban_until DATETIME"))
        print("Added ban_until to 'user'")
    except Exception as e:
        print(f"ban_until may already exist or error: {e}")
        
    try:
        db.session.execute(text("ALTER TABLE user ADD COLUMN trust_score INTEGER DEFAULT 100"))
        print("Added trust_score to 'user'")
    except Exception as e:
        print(f"trust_score may already exist or error: {e}")

    # Check 'item' table
    try:
        db.session.execute(text("ALTER TABLE item ADD COLUMN status VARCHAR(20) DEFAULT 'Open'"))
        print("Added status to 'item'")
    except Exception as e:
        print(f"status may already exist or error: {e}")

    db.session.commit()
    print("Migration SUCCESSful using app context!")
