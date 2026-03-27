"""
User Preference Models for Notifications (Mute/Block)
"""
from app.extensions import db

class MutedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'item_id', name='_user_item_mute_uc'),)
    
    user = db.relationship('User', backref=db.backref('muted_items', lazy='dynamic', cascade="all, delete-orphan"))
    item = db.relationship('Item', backref=db.backref('muted_by', lazy='dynamic', cascade="all, delete-orphan"))

class BlockedUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # User who blocks
    blocked_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # User who is blocked
    __table_args__ = (db.UniqueConstraint('user_id', 'blocked_user_id', name='_user_user_block_uc'),)
    
    blocking_user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('blocked_users_list', lazy='dynamic', cascade="all, delete-orphan"))
    blocked_user = db.relationship('User', foreign_keys=[blocked_user_id], backref=db.backref('blocked_by_list', lazy='dynamic', cascade="all, delete-orphan"))
