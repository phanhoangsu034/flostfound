from app import app, db
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE user ADD COLUMN avatar VARCHAR(200)"))
            print("Successfully added avatar column to user table.")
        except Exception as e:
            print(f"Column might already exist or error occurred: {e}")
