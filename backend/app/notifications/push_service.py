"""
FCM Push Notification Service
Xử lý lưu FCM token và gửi push notification qua Firebase Admin SDK
"""
import os
import json
import logging

logger = logging.getLogger(__name__)

# Firebase Admin SDK - lazy init để tránh lỗi nếu chưa cấu hình
_firebase_app = None


def _get_firebase_app():
    """Khởi tạo Firebase Admin App (lazy)"""
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app

    try:
        import firebase_admin
        from firebase_admin import credentials

        # Ưu tiên dùng file JSON service account
        service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH')
        service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')

        if service_account_path and os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
        elif service_account_json:
            # Trường hợp deploy Railway/Render: lưu JSON vào env var
            service_account_info = json.loads(service_account_json)
            cred = credentials.Certificate(service_account_info)
        else:
            logger.warning("⚠️  Firebase: Không tìm thấy SERVICE ACCOUNT. Push notification sẽ KHÔNG hoạt động.")
            logger.warning("⚠️  Set FIREBASE_SERVICE_ACCOUNT_PATH hoặc FIREBASE_SERVICE_ACCOUNT_JSON trong .env")
            return None

        if not firebase_admin._apps:
            _firebase_app = firebase_admin.initialize_app(cred)
        else:
            _firebase_app = firebase_admin.get_app()

        logger.info("✅ Firebase Admin SDK khởi tạo thành công!")
        return _firebase_app

    except ImportError:
        logger.error("❌ firebase-admin chưa được cài đặt! Chạy: pip install firebase-admin")
        return None
    except Exception as e:
        logger.error(f"❌ Lỗi khởi tạo Firebase: {e}")
        return None


def send_push_notification(token: str, title: str, body: str, data: dict = None, url: str = '/') -> bool:
    """
    Gửi push notification đến một FCM token cụ thể
    
    Args:
        token: FCM token của thiết bị
        title: Tiêu đề notification
        body: Nội dung notification  
        data: Dict data bổ sung (optional)
        url: URL để mở khi click notification
    
    Returns:
        True nếu thành công, False nếu thất bại
    """
    firebase_app = _get_firebase_app()
    if firebase_app is None:
        return False

    try:
        from firebase_admin import messaging

        # Tạo notification payload
        notification = messaging.Notification(
            title=title,
            body=body
        )

        # Web-specific config
        webpush_config = messaging.WebpushConfig(
            notification=messaging.WebpushNotification(
                title=title,
                body=body,
                icon='/static/icons/icon-192x192.png',
                badge='/static/icons/badge-72x72.png',
                vibrate=[200, 100, 200],
                actions=[
                    messaging.WebpushNotificationAction(action='open', title='Mở ngay'),
                    messaging.WebpushNotificationAction(action='dismiss', title='Bỏ qua'),
                ]
            ),
            fcm_options=messaging.WebpushFCMOptions(link=url)
        )

        # Custom data
        custom_data = {'url': url, **(data or {})}
        # FCM data values must be strings
        string_data = {k: str(v) for k, v in custom_data.items()}

        message = messaging.Message(
            notification=notification,
            webpush=webpush_config,
            data=string_data,
            token=token,
        )

        response = messaging.send(message)
        logger.info(f"✅ Push sent successfully: {response}")
        return True

    except Exception as e:
        error_str = str(e)
        logger.error(f"❌ Error sending push to token {token[:20]}...: {e}")
        return False


def send_push_to_user(user_id: int, title: str, body: str, data: dict = None, url: str = '/') -> int:
    """
    Gửi push notification đến TẤT CẢ thiết bị của một user
    
    Args:
        user_id: ID của user
        title, body, data, url: như send_push_notification
    
    Returns:
        Số lượng push gửi thành công
    """
    from app.models.fcm_token import FCMToken

    tokens = FCMToken.query.filter_by(user_id=user_id).all()
    if not tokens:
        logger.debug(f"User {user_id} chưa đăng ký FCM token")
        return 0

    success_count = 0
    failed_tokens = []

    for fcm_token in tokens:
        success = send_push_notification(
            token=fcm_token.token,
            title=title,
            body=body,
            data=data,
            url=url
        )
        if success:
            success_count += 1
        else:
            failed_tokens.append(fcm_token)

    # Xóa các token bị invalid (expired/unregistered)
    if failed_tokens:
        from app.extensions import db
        for bad_token in failed_tokens:
            db.session.delete(bad_token)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cleaning up bad tokens: {e}")

    return success_count
