"""
Login routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user
from app.models.user import User

bp = Blueprint('auth_login', __name__)

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
