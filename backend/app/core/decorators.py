"""
Core decorators for the application
"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, 'level', 3) > 2:
            flash('Bạn không có quyền truy cập trang này. Vui lòng liên hệ quản trị viên.', 'danger')
            return redirect(url_for('posts_view.index'))
        return f(*args, **kwargs)
    return decorated_function
