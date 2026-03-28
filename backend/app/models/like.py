"""
Like model for posts
"""
from datetime import datetime
from app.extensions import db

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_liked = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'item_id', name='_user_item_like_uc'),)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('likes', lazy='dynamic', cascade="all, delete-orphan"))
    item = db.relationship('Item', backref=db.backref('likes', lazy='dynamic', cascade="all, delete-orphan"))
