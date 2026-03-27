"""
Report model
"""
from datetime import datetime
from app.extensions import db

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_type = db.Column(db.String(50), nullable=False) # 'comment', 'user', 'item'
    reported_id = db.Column(db.Integer, nullable=False) # Generic ID based on type
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, resolved, dismissed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
