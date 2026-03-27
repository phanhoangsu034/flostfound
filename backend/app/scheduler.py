"""
Scheduler jobs for auto-expiring posts
"""
import requests
import json
from datetime import datetime, timedelta
from app.extensions import db
from app.models.item import Item
from app.models.notification import Notification

def send_emailjs_warning(email, name, item_title):
    """
    Gửi email cảnh báo qua EmailJS REST API
    Cần thay thế SERVICE_ID, TEMPLATE_ID, USER_ID (Public Key) phù hợp.
    """
    url = "https://api.emailjs.com/api/v1.0/email/send"
    
    # [TO-DO] Thay thế bằng credential thật của EmailJS cho Template cảnh báo
    data = {
        "service_id": "service_263jx3i", # Dùng tạm service ID đang có
        "template_id": "template_1gblxih", # KHUYẾN NGHỊ: Tạo template mới trên EmailJS
        "user_id": "FiWoCZgxcRcbBod10", # Public Key
        "template_params": {
            "to_email": email,
            "to_name": name,
            "reset_link": f"Bài viết '{item_title}' của bạn sắp bị xóa sau 5 ngày. Vui lòng vào trang web để gia hạn!" # Dùng tạm biến reset_link để truyền text
        }
    }
    
    try:
        requests.post(url, json=data)
    except Exception as e:
        print("Lỗi gửi email cảnh báo:", e)

def check_expiring_posts(app):
    """Job chạy định kỳ kiểm tra bài viết sắp hết hạn"""
    with app.app_context():
        now = datetime.utcnow()
        # Lấy tất cả bài viết còn Open
        items = Item.query.filter_by(status='Open').all()
        
        for item in items:
            # Tính ngày hết hạn
            expiry_date = item.expires_at if item.expires_at else item.date_posted + timedelta(days=20)
            
            # Thời điểm cần gửi cảnh báo (5 ngày trước khi hết) -> 15 ngày sau khi đăng/gia hạn
            warning_date = expiry_date - timedelta(days=5)
            
            # 1. Nếu đã qua ngày hết hạn -> Xóa bài
            if now >= expiry_date:
                # Tạo thông báo đã xóa vào chuông báo
                notif = Notification(
                    recipient_id=item.user_id,
                    action_type='system',
                    content=f'Bài viết "{item.title[:30]}..." đã tự động bị xóa do quá hạn 20 ngày không tương tác.'
                )
                db.session.add(notif)
                
                # Xóa item (cascade sẽ lo comments/likes/images)
                db.session.delete(item)
                db.session.commit()
                continue
                
            # 2. Nếu đã qua ngày cần cảnh báo và chưa gửi cảnh báo -> Gửi cảnh báo
            if now >= warning_date and not item.warning_sent:
                item.warning_sent = True
                
                # Tạo thông báo chuông
                notif = Notification(
                    recipient_id=item.user_id,
                    item_id=item.id,
                    action_type='expiry_warning',
                    content=f'Bài viết "{item.title[:20]}..." sẽ tự động bị xóa sau 5 ngày. Vui lòng gia hạn nếu chưa tìm thấy đồ!'
                )
                db.session.add(notif)
                
                # Gửi email thực qua EmailJS
                send_emailjs_warning(item.user.email, item.user.username, item.title)
                
                # Phát qua socketio luôn nếu user đang online
                try:
                    from app.extensions import socketio
                    socketio.emit('notification', {
                        'message': notif.content,
                        'sender_name': 'Hệ thống',
                        'type': 'new_notification'
                    }, room=f'user_{item.user_id}')
                except Exception:
                    pass
                
                db.session.commit()

def delete_closed_posts(app):
    """Job kiểm tra và xóa các bài viết đã hoàn trả (Closed) quá 5 ngày"""
    with app.app_context():
        # Tìm bài viết Closed
        closed_items = Item.query.filter_by(status='Closed').all()
        now = datetime.utcnow()
        for item in closed_items:
            # Nếu đã closed quá 5 ngày (Tính từ incident_date hoặc logic khác, 
            # ở đây tạm dùng date_posted + 5 ngày từ lúc nó chuyển Closed - 
            # nhưng model chưa lưu ngày chuyển Closed. Để đơn giản, giả thiết user cập nhật status 
            # -> ta có thể lưu closed_at hoặc tính 5 ngày từ lúc phát hiện.
            # Do không có cột closed_at, ta cho phép lưu thời gian hết hạn hoặc tạm skip xóa vĩnh viễn
            # nếu quá 5 ngày kể từ date_posted).
            # [SỬA ĐỔI]: Tạm thời ẩn khỏi bảng feed đã được thực hiện bằng query post_status != Closed.
            # Để xóa sau 5 ngày, ta tính từ cột expires_at (khi user đánh dấu Closed, set expires_at = now + 5 days) 
            if item.expires_at and now >= item.expires_at:
                db.session.delete(item)
        db.session.commit()

def start_scheduler(app):
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler(daemon=True)
    
    # Chạy mỗi giờ 1 lần
    scheduler.add_job(func=lambda: check_expiring_posts(app), trigger="interval", hours=1)
    scheduler.add_job(func=lambda: delete_closed_posts(app), trigger="interval", hours=1)
    
    scheduler.start()
