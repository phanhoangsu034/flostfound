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
        new_user.auth_provider = 'google'
        
        # Đặt 1 mật khẩu random cực khó - Khóa chết việc đăng nhập tay
        random_password = secrets.token_urlsafe(16)
        new_user.set_password(random_password)
        
        db.session.add(new_user)
        db.session.commit()
        user = new_user
    else:
        # Nếu tài khoản đã được đăng ký theo cách thông thường (local)
        if getattr(user, 'auth_provider', 'local') == 'local':
             return jsonify({
                 'success': False, 
                 'message': 'Email này đã được đăng ký bằng mật khẩu. Vui lòng đăng nhập bằng email và mật khẩu.'
             })
             
        # Nếu tài khoản đã có (và là google), cập nhật avatar
        user.avatar_url = avatar or user.avatar_url
        user.auth_provider = 'google'
        db.session.commit()

    # 3. Đăng nhập cho cả Acc cũ lẫn mới
    login_user(user, remember=True)
    flash("Đăng nhập thành công. Chào mừng bạn quay lại!", "success")
    return jsonify({'success': True, 'redirect': url_for('posts_view.index')})

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Tên đăng nhập không tồn tại.', 'danger')
        elif not user.check_password(password):
            flash('Mật khẩu không chính xác.', 'danger')
        else:
            login_user(user, remember=True)
            return redirect(url_for('posts_view.index'))
            
    return render_template('auth/login.html')
