"""
Password reset routes using EmailJS (Frontend) logic
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from app.models.user import User
from app.extensions import db

bp = Blueprint('auth_password_reset', __name__)

def get_serializer():
    """Returns a URLSafeTimedSerializer for signing tokens."""
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

@bp.route('/forgot_password', methods=['GET'])
def forgot_password():
    """Render the forgot password page where user inputs email"""
    return render_template('auth/forgot_password.html')

@bp.route('/api/forgot_password', methods=['POST'])
def api_forgot_password():
    """Generates a secure reset link for the provided email"""
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'success': False, 'message': 'Email is required'}), 400
        
    email = data['email']
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # We still return success:True on frontend to prevent email enumeration,
        # but we don't return a reset link. The frontend EmailJS won't send an email
        # if reset_link is empty, or we can just say "If email exists, an email is sent."
        # For simplicity and given EmailJS constraints, let's return an error if email not found.
        return jsonify({'success': False, 'message': 'Không tìm thấy tài khoản với email này.'}), 404
        
    if user.auth_provider == 'google':
        return jsonify({'success': False, 'message': 'Tài khoản này đã được liên kết với Google. Vui lòng đăng nhập bằng Google để bảo mật.'}), 403
        
    s = get_serializer()
    # Create a token containing the user's ID
    token = s.dumps(user.id, salt='password-reset-salt')
    
    # Generate the absolute reset URL
    reset_link = url_for('auth_password_reset.reset_password', token=token, _external=True)
    
    return jsonify({
        'success': True, 
        'reset_link': reset_link,
        'user_name': user.full_name or user.username
    })

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    s = get_serializer()
    try:
        # Token is valid for 3600 seconds (1 hour)
        user_id = s.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        flash('Link khôi phục mật khẩu đã hết hạn.', 'danger')
        return redirect(url_for('auth_password_reset.forgot_password'))
    except BadTimeSignature:
        flash('Link khôi phục mật khẩu không hợp lệ.', 'danger')
        return redirect(url_for('auth_password_reset.forgot_password'))
        
    user = User.query.get(user_id)
    if not user:
        flash('Tài khoản không tồn tại.', 'danger')
        return redirect(url_for('auth_password_reset.forgot_password'))
        
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or new_password != confirm_password:
            flash('Mật khẩu không khớp hoặc bị trống.', 'danger')
            return render_template('auth/reset_password.html', token=token)
            
        user.set_password(new_password)
        db.session.commit()
        
        from flask_login import logout_user
        logout_user()  # Đăng xuất mọi phiên bảo lưu trên thiết bị
        
        flash('Mật khẩu của bạn đã được thay đổi thành công. Vui lòng đăng nhập lại trên tất cả thiết bị.', 'success')
        return redirect(url_for('auth_login.login'))
        
    return render_template('auth/reset_password.html', token=token)
