"""
Comment model for posts
"""
from datetime import datetime
from app.extensions import db

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    item = db.relationship('Item', backref=db.backref('comments', lazy='dynamic', cascade="all, delete-orphan"))

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'date_posted': self.date_posted.isoformat() + 'Z',
            'user_id': self.user_id,
            'username': self.user.username,
            'user_avatar': self.user.avatar,
            'item_id': self.item_id
        }
