"""
User model
"""
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    # Core fields
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    auth_provider = db.Column(db.String(50), default='local')

    # Profile fields
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    avatar_url = db.Column(db.String(300), default='')
    about_me = db.Column(db.Text)

    # System fields
    is_admin = db.Column(db.Boolean, default=False)
    level = db.Column(db.Integer, default=3) # 1: Super Admin, 3: User
    is_banned = db.Column(db.Boolean, default=False)
    ban_until = db.Column(db.DateTime, nullable=True) # If null and is_banned=True, then permanent
    trust_score = db.Column(db.Integer, default=100) # 0-100 scale
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Password helpers ---
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    # --- Avatar helper ---
    @property
    def avatar(self):
        """Return avatar URL or initials placeholder."""
        if self.avatar_url:
            return self.avatar_url
        return f"https://ui-avatars.com/api/?name={self.username}&background=F27123&color=fff&size=128"
