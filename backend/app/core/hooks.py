"""
Core application hooks (before_request, user_loader, etc.)
"""
from datetime import datetime
from flask_login import current_user
from app.extensions import db, login_manager
from app.models.user import User

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

def register_hooks(app):
    """Register application hooks"""
    
    @app.before_request
    def before_request():
        """Update user's last_seen timestamp and handle banning logic before each request"""
        if current_user.is_authenticated:
            # 1. Update last seen
            current_user.last_seen = datetime.utcnow()
            
            # 2. Check if the user's ban has expired
            if current_user.is_banned and current_user.ban_until:
                if current_user.ban_until < datetime.utcnow():
                    current_user.is_banned = False
                    current_user.ban_until = None
                    db.session.commit()
            
            # 3. If still banned, logout (or prevent access)
            if current_user.is_banned:
                from flask_login import logout_user
                from flask import flash, redirect, url_for
                ban_msg = "Tài khoản của bạn đã bị khóa."
                if current_user.ban_until:
                    ban_msg += f" (Hết hạn lúc {current_user.ban_until.strftime('%H:%M %d/%m/%Y')})"
                else:
                    ban_msg += " (Khóa vĩnh viễn)"
                
                logout_user()
                flash(ban_msg, 'danger')
                return redirect(url_for('auth_login.login'))

            db.session.commit()

    @app.context_processor
    def inject_unread_count():
        """Inject unread message count into all templates"""
        if current_user.is_authenticated:
            from app.models.message import Message 
            count = Message.query.filter_by(recipient_id=current_user.id, is_read=False).count()
            return dict(unread_count=count)
        return dict(unread_count=0)
