"""
Chat routes
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.models.user import User
from app.models.message import Message
import cloudinary.uploader

bp = Blueprint('messages_chat', __name__)

@bp.route('/chat/<int:recipient_id>')
@login_required
def chat(recipient_id):
    recipient = User.query.get_or_404(recipient_id)
    # Get history
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == recipient_id)) |
        ((Message.sender_id == recipient_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()
    
    # Mark unread messages from this sender as read
    unread_msgs = Message.query.filter_by(sender_id=recipient_id, recipient_id=current_user.id, is_read=False).all()
    if unread_msgs:
        for msg in unread_msgs:
            msg.is_read = True
        try:
            from app.extensions import db
            db.session.commit()
        except:
             db.session.rollback()
    
    return render_template('messages/chat.html', recipient=recipient, messages=messages, datetime=datetime)

@bp.route('/api/messages/send_simple', methods=['POST'])
@login_required
def send_simple_message():
    from flask import request, jsonify
    from app.models.message import Message
    from app.extensions import db
    
    data = request.get_json()
    recipient_id = data.get('recipient_id')
    body = data.get('message')
    
    if not recipient_id or not body:
        return jsonify({'success': False, 'message': 'Thiếu thông tin'})
        
    msg = Message(sender_id=current_user.id, recipient_id=recipient_id, body=body)
    db.session.add(msg)
    
    # Notifications
    from app.models.notification import Notification
    from datetime import datetime
    existing_notif = Notification.query.filter_by(
        recipient_id=recipient_id,
        actor_id=current_user.id,
        action_type='message',
        is_read=False
    ).first()
    
    msg_preview = body[:40] + '...' if len(body) > 40 else body
    if existing_notif:
        existing_notif.created_at = datetime.utcnow()
        existing_notif.content = f'Đã gửi cho bạn một tin nhắn: "{msg_preview}"'
    else:
        notif = Notification(
            recipient_id=recipient_id,
            actor_id=current_user.id,
            action_type='message',
            content=f'Đã gửi cho bạn một tin nhắn: "{msg_preview}"'
        )
        db.session.add(notif)

    db.session.commit()
    
    return jsonify({'success': True})

@bp.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "Vui lòng chọn ảnh."}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "Tập tin rỗng."}), 400
        
    # CẢI TIẾN BẢO MẬT 1: Chống upload file độc hại (Chỉ nhận Ảnh)
    if not file.mimetype.startswith('image/'):
        return jsonify({"error": "Hệ thống chỉ chấp nhận định dạng Ảnh!"}), 400
        
    # CẢI TIẾN BẢO MẬT 2: Giới hạn dung lượng <= 5MB (Chống đầy băng thông cục bộ Cloudinary)
    file.seek(0, 2) # Dò con trỏ đến đích để đọc ra kích thước Bytes
    file_length = file.tell()
    file.seek(0) # Bắt buộc phải reset lại con trỏ file, nếu không cloudinary upload sẽ lỗi ảnh rỗng
    
    if file_length > 5 * 1024 * 1024:
        return jsonify({"error": "Dung lượng ảnh tải lên không được vượt quá 5MB!"}), 400
        
    try:
        # Thêm vào folder flostfound/messages trên cloudinary
        result = cloudinary.uploader.upload(file, folder="flostfound/messages")
        return jsonify({"url": result['secure_url']})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Lỗi máy chủ khi tải ảnh."}), 500
