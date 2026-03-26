from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile fields
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    avatar_url = db.Column(db.String(300), default='')
    about_me = db.Column(db.Text)
    
    # System fields
    is_admin = db.Column(db.Boolean, default=False)
    level = db.Column(db.Integer, default=3) # 1: Super Admin, 2: Moderator, 3: User
    is_banned = db.Column(db.Boolean, default=0)
    ban_until = db.Column(db.DateTime, nullable=True)
    trust_score = db.Column(db.Integer, default=100)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def avatar(self):
        if self.avatar_url:
            return self.avatar_url
        return f"https://ui-avatars.com/api/?name={self.username}&background=RANDOM&color=fff"

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    item_type = db.Column(db.String(10)) # 'Lost' or 'Found'
    image_url = db.Column(db.String(300))
    status = db.Column(db.String(20), default='Open') # 'Open' or 'Closed'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('items', lazy=True))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

class ActionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('logs', lazy=True))
