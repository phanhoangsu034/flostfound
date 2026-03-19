"""
SocketIO events for real-time messaging
"""
from flask_login import current_user
from flask_socketio import emit, join_room
from app.extensions import socketio, db
from app.models.message import Message

@socketio.on('join_notifications')
def on_join_notifications():
    if current_user.is_authenticated:
        room = f"user_{current_user.id}"
        join_room(room)

@socketio.on('send_message')
def handle_message(data):
    # data = {recipient_id, message}
    recipient_id = data.get('recipient_id')
    body = data.get('message')
    
    if not current_user.is_authenticated:
        return
        
    msg = Message(sender_id=current_user.id, recipient_id=recipient_id, body=body)
    db.session.add(msg)
    db.session.commit()
    
    room = f"chat_{min(current_user.id, int(recipient_id))}_{max(current_user.id, int(recipient_id))}"
    emit('receive_message', {
        'sender_id': current_user.id,
        'message': body,
        'timestamp': msg.timestamp.isoformat() + 'Z'
    }, room=room)
    
    # Emit notification to recipient's private room
    notification_room = f"user_{recipient_id}"
    emit('notification', {
        'sender_id': current_user.id,
        'sender_name': current_user.username,
        'message': body
    }, room=notification_room)

@socketio.on('join_chat')
def on_join(data):
    recipient_id = data.get('recipient_id')
    room = f"chat_{min(current_user.id, int(recipient_id))}_{max(current_user.id, int(recipient_id))}"
    join_room(room)

# ==========================================
# WebRTC SIGNALING LOGIC (Video/Voice Call)
# ==========================================

def save_call_log(sender_id, recipient_id, body):
    """ Hàm hộ trợ ghi dấu vết cuộc gọi vào DB thành tin nhắn hệ thống """
    msg = Message(sender_id=sender_id, recipient_id=recipient_id, body=body)
    db.session.add(msg)
    db.session.commit()
    
    room = f"chat_{min(sender_id, int(recipient_id))}_{max(sender_id, int(recipient_id))}"
    emit('receive_message', {
        'sender_id': sender_id,
        'message': body,
        'timestamp': msg.timestamp.isoformat() + 'Z'
    }, room=room)
    
    # Báo luôn cho room riêng để nổi bong bóng unread notification
    notification_room = f"user_{recipient_id}"
    emit('notification', {
        'sender_id': sender_id,
        'sender_name': 'Hệ thống',
        'message': body
    }, room=notification_room)

@socketio.on('call_user')
def on_call_user(data):
    """ Người A gửi yêu cầu gọi (Offer) cho người B """
    if not current_user.is_authenticated: return
    
    user_to_call = data.get('user_to_call')
    signal_data = data.get('signal_data')
    is_video = data.get('is_video', True)
    
    room = f"user_{user_to_call}"
    emit('call_made', {
        'signal': signal_data,
        'from': current_user.id,
        'from_name': current_user.username,
        'from_avatar': current_user.avatar,
        'is_video': is_video
    }, room=room)


@socketio.on('user_busy')
def on_user_busy(data):
    """ Người B phản hồi lại là đang bận cuộc gọi khác """
    if not current_user.is_authenticated: return
    to_user = data.get('to')
    room = f"user_{to_user}"
    emit('call_busy', {'from': current_user.id}, room=room)


@socketio.on('make_answer')
def on_make_answer(data):
    """ Người B chấp nhận và gửi Phản hồi (Answer) lại cho A """
    if not current_user.is_authenticated: return
    
    to_user = data.get('to')
    signal_data = data.get('signal')
    
    room = f"user_{to_user}"
    emit('answer_made', {
        'signal': signal_data,
        'to': current_user.id
    }, room=room)

@socketio.on('ice_candidate')
def on_ice_candidate(data):
    """ Trung chuyển thông tin mạng ICE Candidate cho 2 máy kết nối P2P """
    if not current_user.is_authenticated: return
    
    to_user = data.get('to')
    candidate = data.get('candidate')
    
    room = f"user_{to_user}"
    emit('ice_candidate', {
        'candidate': candidate,
        'from': current_user.id
    }, room=room)

@socketio.on('reject_call')
def on_reject_call(data):
    """ Xử lý khi người B Ấn nút Từ Chối """
    if not current_user.is_authenticated: return
    
    to_user = data.get('to')
    room = f"user_{to_user}"
    
    save_call_log(current_user.id, to_user, "📞 Cuộc gọi bị từ chối")
    
    emit('call_rejected', {
        'from': current_user.id
    }, room=room)

@socketio.on('end_call')
def on_end_call(data):
    """ Xử lý khi đang gọi mà Cúp máy (Ngắt cuộc gọi hoặc Cuộc gọi nhỡ) """
    if not current_user.is_authenticated: return
    
    to_user = data.get('to')
    duration = data.get('duration', 0)
    
    if duration == 0:
        body = "📞 Cuộc gọi nhỡ"
    else:
        m, s = divmod(duration, 60)
        body = f"📞 Cuộc gọi video kết thúc - {m:02d}:{s:02d}"
        
    save_call_log(current_user.id, to_user, body)
    
    room = f"user_{to_user}"
    emit('call_ended', {
        'from': current_user.id
    }, room=room)
