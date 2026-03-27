"""
Notification Routes:
- POST /save-fcm-token   : Nhận và lưu FCM token từ frontend
- GET  /firebase-messaging-sw.js : Serve service worker (phải ở root domain!)
- POST /test-push        : Admin route để test gửi push (dev only)
"""
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_login import login_required, current_user
import os
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('notifications', __name__)


@bp.route('/firebase-messaging-sw.js')
def serve_firebase_sw():
    """
    QUAN TRỌNG: Service Worker phải được serve từ root domain
    Flask dùng /static/ nhưng SW cần ở /firebase-messaging-sw.js
    Route này giải quyết vấn đề đó.
    """
    static_dir = os.path.join(current_app.root_path, '..', '..', 'frontend', 'static')
    static_dir = os.path.abspath(static_dir)
    
    response = send_from_directory(static_dir, 'firebase-messaging-sw.js')
    # Service Worker phải có Content-Type đúng
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response


@bp.route('/save-fcm-token', methods=['POST'])
@login_required
def save_fcm_token():
    """
    Nhận FCM token từ frontend và lưu vào DB
    Body: { "token": "FCM_TOKEN_STRING" }
    """
    data = request.get_json(silent=True)
    if not data or 'token' not in data:
        return jsonify({'error': 'Missing token'}), 400

    token = data['token'].strip()
    if not token:
        return jsonify({'error': 'Empty token'}), 400

    try:
        from app.models.fcm_token import FCMToken
        from app.extensions import db

        # Kiểm tra token đã tồn tại chưa (nhiều user, nhiều thiết bị)
        existing = FCMToken.query.filter_by(token=token).first()
        
        if existing:
            if existing.user_id != current_user.id:
                # Token này đang thuộc user khác → chuyển sang user hiện tại
                existing.user_id = current_user.id
                db.session.commit()
                logger.info(f"FCM token migrated to user {current_user.id}")
            else:
                logger.debug(f"FCM token already registered for user {current_user.id}")
        else:
            # Token mới → lưu vào DB
            new_token = FCMToken(user_id=current_user.id, token=token)
            db.session.add(new_token)
            db.session.commit()
            logger.info(f"✅ New FCM token saved for user {current_user.id}")

        return jsonify({'success': True, 'message': 'Token đã được lưu'}), 200

    except Exception as e:
        logger.error(f"Error saving FCM token: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/delete-fcm-token', methods=['POST'])
@login_required
def delete_fcm_token():
    """
    Xóa FCM token khi user logout hoặc từ chối quyền notification
    Body: { "token": "FCM_TOKEN_STRING" }
    """
    data = request.get_json(silent=True)
    if not data or 'token' not in data:
        return jsonify({'error': 'Missing token'}), 400

    try:
        from app.models.fcm_token import FCMToken
        from app.extensions import db

        FCMToken.query.filter_by(
            token=data['token'],
            user_id=current_user.id
        ).delete()
        db.session.commit()
        return jsonify({'success': True}), 200

    except Exception as e:
        logger.error(f"Error deleting FCM token: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/test-push', methods=['POST'])
@login_required
def test_push():
    """
    Route DEV: Test gửi push đến chính mình
    Body: { "title": "...", "body": "..." }
    """
    if not current_app.debug and not current_user.is_admin:
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json(silent=True) or {}
    title = data.get('title', '🔔 Test Push từ F-LostFound')
    body = data.get('body', 'Push notification đang hoạt động!')

    try:
        from app.notifications.push_service import send_push_to_user
        count = send_push_to_user(
            user_id=current_user.id,
            title=title,
            body=body,
            url='/messages'
        )
        return jsonify({
            'success': True,
            'sent_count': count,
            'message': f'Đã gửi tới {count} thiết bị'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Lấy danh sách thông báo của người dùng hiện tại"""
    from app.models.notification import Notification
    
    # Lấy 30 thông báo mới nhất
    notifications = Notification.query.filter_by(recipient_id=current_user.id).order_by(Notification.created_at.desc()).limit(30).all()
    
    return jsonify({
        'success': True,
        'notifications': [n.to_dict() for n in notifications],
        'unread_count': Notification.query.filter_by(recipient_id=current_user.id, is_read=False).count()
    })

@bp.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
def mark_read(notif_id):
    """Đánh dấu 1 thông báo là đã đọc"""
    from app.models.notification import Notification
    from app.extensions import db
    
    notif = Notification.query.filter_by(id=notif_id, recipient_id=current_user.id).first()
    if notif and not notif.is_read:
        notif.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Không tìm thấy hoặc đã đọc'}), 404

@bp.route('/api/notifications/read_all', methods=['POST'])
@login_required
def mark_all_read():
    """Đánh dấu tất cả thông báo là đã đọc"""
    from app.models.notification import Notification
    from app.extensions import db
    
    unread = Notification.query.filter_by(recipient_id=current_user.id, is_read=False).all()
    for n in unread:
        n.is_read = True
        
    db.session.commit()
    return jsonify({'success': True})
