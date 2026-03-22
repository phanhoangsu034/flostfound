"""
Registration routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
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
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email này đã được sử dụng.'})
        
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

        if User.query.filter_by(email=email).first():
            flash('Email này đã được sử dụng.', 'danger')
            return redirect(url_for('auth_register.register'))
            
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Tạo tài khoản thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth_login.login'))
        
    return render_template('auth/register.html')
