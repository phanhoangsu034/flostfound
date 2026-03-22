"""
FCM Token model - lưu Firebase Cloud Messaging token của từng user
"""
from app.extensions import db
from datetime import datetime


class FCMToken(db.Model):
    """Lưu FCM push token của mỗi thiết bị/browser của user"""
    __tablename__ = 'fcm_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    token = db.Column(db.Text, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Quan hệ với User
    user = db.relationship('User', backref=db.backref('fcm_tokens', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<FCMToken user_id={self.user_id} token={self.token[:20]}...>'
