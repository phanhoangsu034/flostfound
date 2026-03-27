"""
Notification model
"""
from datetime import datetime
from app.extensions import db

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Could be system notification
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    
    action_type = db.Column(db.String(50), nullable=False) # 'like', 'comment', 'tag'
    content = db.Column(db.String(255), nullable=True)     # E.g., The comment snippet or message
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional direct link to comment
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'), nullable=True)

    recipient = db.relationship('User', foreign_keys=[recipient_id], backref=db.backref('notifications', lazy='dynamic', cascade="all, delete-orphan"))
    actor = db.relationship('User', foreign_keys=[actor_id])
    item = db.relationship('Item', backref=db.backref('notifications', lazy='dynamic', cascade="all, delete-orphan"))
    comment = db.relationship('Comment', backref=db.backref('notifications', lazy='dynamic', cascade="all, delete-orphan"))

    def to_dict(self):
        return {
            'id': self.id,
            'action_type': self.action_type,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() + 'Z',
            'actor_id': self.actor_id,
            'actor_name': self.actor.username if self.actor else 'Hệ thống',
            'actor_avatar': self.actor.avatar if self.actor else '',
            'item_id': self.item_id,
            'item_title': self.item.title if self.item else None,
            'comment_id': self.comment_id
        }
