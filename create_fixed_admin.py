import sys
import os

# Set current path for imports to find 'backend' module
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from app.extensions import db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Use standard admin/123456 as requested by user
    admin_user = "admin"
    admin_pass = "123456"

    # Check if 'admin' exists
    admin = User.query.filter_by(username=admin_user).first()
    if admin:
        print(f"Admin user '{admin_user}' exists. Resetting password and permissions...")
        admin.set_password(admin_pass)
        admin.is_admin = True
        admin.is_banned = False
        db.session.commit()
        print(f"Admin '{admin_user}' updated.")
    else:
        print(f"Creating NEW admin user '{admin_user}'...")
        new_admin = User(
            username=admin_user,
            email='admin@fpt.edu.vn'
        )
        new_admin.set_password(admin_pass)
        new_admin.is_admin = True
        new_admin.is_banned = False
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin '{admin_user}' created successfully.")

print("\nPROCESS COMPLETED.")
