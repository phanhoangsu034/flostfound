"""
Registration routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user
from app.extensions import db
from app.models.user import User

bp = Blueprint('auth_register', __name__)

@bp.route('/api/check_register', methods=['POST'])
def check_register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Tên đăng nhập đã tồn tại.'})

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        if getattr(existing_user, 'auth_provider', 'local') == 'google':
            return jsonify({'success': False, 'message': 'Email này đã được đăng ký bằng Google. Vui lòng chọn "Đăng nhập với Google".'})
        else:
            created_at_fmt = existing_user.created_at.strftime('%d/%m/%Y')
            return jsonify({'success': False, 'message': f'Email này đã được đăng ký từ ngày {created_at_fmt}. Vui lòng đăng nhập hoặc chọn "Quên mật khẩu".'})
        
    return jsonify({'success': True})

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại.', 'danger')
            return redirect(url_for('auth_register.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if getattr(existing_user, 'auth_provider', 'local') == 'google':
                flash('Email này đã được đăng ký bằng Google. Vui lòng chọn "Đăng nhập với Google".', 'danger')
            else:
                created_at_fmt = existing_user.created_at.strftime('%d/%m/%Y')
                flash(f'Email này đã được đăng ký từ ngày {created_at_fmt}. Vui lòng đăng nhập hoặc chọn "Quên mật khẩu".', 'danger')
            return redirect(url_for('auth_register.register'))
            
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # Tự động đăng nhập người dùng ngay sau khi đăng ký
        login_user(new_user)
        
        flash('Đăng ký thành công! Chào mừng bạn.', 'success')
        return redirect(url_for('posts_view.index'))
        
    return render_template('auth/register.html')
