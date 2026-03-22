"""
Login routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user
from app.models.user import User
from app.extensions import db
import secrets

bp = Blueprint('auth_login', __name__)

@bp.route('/api/social_login', methods=['POST'])
def social_login():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    avatar = data.get('avatar', '')

    if not email:
        return jsonify({'success': False, 'message': 'Không tìm thấy Email từ provider'})

    # 1. Kiểm tra tài khoản đã tồn tại
    user = User.query.filter_by(email=email).first()
    
    # 2. Tạo tài khoản mới nếu chưa có
    if not user:
        # Xử lý Username tránh bị trùng lặp Database
        base_username = name.replace(" ", "").lower() if name else email.split('@')[0]
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
            
        new_user = User(email=email, username=username, full_name=name)
        new_user.avatar_url = avatar
        
        # Đặt 1 mật khẩu random cực khó - Khóa chết việc đăng nhập tay
        random_password = secrets.token_urlsafe(16)
        new_user.set_password(random_password)
        
        db.session.add(new_user)
        db.session.commit()
        user = new_user

    # 3. Đăng nhập cho cả Acc cũ lẫn mới
    login_user(user)
    return jsonify({'success': True, 'redirect': url_for('posts_view.index')})

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('posts_view.index'))
        else:
            flash('Đăng nhập thất bại. Kiểm tra lại thông tin.', 'danger')
            
    return render_template('auth/login.html')
