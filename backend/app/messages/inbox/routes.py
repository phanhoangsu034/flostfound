"""
Inbox routes
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime
from app.models.user import User
from app.models.message import Message

bp = Blueprint('messages_inbox', __name__)

@bp.route('/messages')
@login_required
def messages_inbox():
    # Find all users involved in conversations with current_user
    # Simple approach: Get all messages involving current_user, order by time desc
    all_msgs = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.timestamp.desc()).all()
    
    conversations = {}
    for msg in all_msgs:
        other_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id
        if other_id not in conversations:
            other_user = User.query.get(other_id)
            if other_user:
                conversations[other_id] = {
                    'user': other_user,
                    'last_message': msg
                }
    
    # Convert to list
    inbox_items = list(conversations.values())
    return render_template('messages/inbox.html', conversations=inbox_items, datetime=datetime)
