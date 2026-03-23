"""
Item model for lost and found posts
"""
from datetime import datetime
from app.extensions import db

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)  # Building/Area e.g. "Alpha"
    specific_location = db.Column(db.String(200), nullable=True) # Specific room/spot e.g. "Room 201"
    category = db.Column(db.String(100), nullable=True) # Category name
    item_type = db.Column(db.String(20), nullable=False)  # "Lost" or "Found"
    contact_info = db.Column(db.String(200), nullable=True) # Deprecated but kept for safety
    phone_number = db.Column(db.String(20), nullable=True)
    facebook_url = db.Column(db.String(500), nullable=True)
    image_url = db.Column(db.String(500), nullable=True) # Primary thumbnail
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    incident_date = db.Column(db.DateTime, nullable=True) # When it happened
    status = db.Column(db.String(20), default='Open') # Open, Closed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('items', lazy=True))
    images_list = db.relationship('ItemImage', backref='item', lazy='dynamic', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'specific_location': self.specific_location,
            'category': self.category,
            'item_type': self.item_type,
            'contact_info': self.contact_info,
            'phone_number': self.phone_number,
            'facebook_url': self.facebook_url,
            'image_url': self.image_url,
            'date_posted': self.date_posted.isoformat() + 'Z',
            'incident_date': self.incident_date.isoformat() if self.incident_date else None,
            'images': [img.image_url for img in self.images_list],
            'user': self.user.username,
            'user_avatar': self.user.avatar, # Use the avatar property for fallback
            'user_id': self.user_id,
            'status': self.status
        }
