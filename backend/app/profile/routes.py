"""
Profile module - routes.py
Handles: view profile, activity, edit profile, change password, about, guide
Validation: VN phone (03x/05x/07x/08x/09x, 10 digits), email syntax+domain check
"""
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.item import Item

bp = Blueprint('profile', __name__)

# ───────────────────────────── Helpers ─────────────────────────────

def validate_phone(phone: str):
    """Validate Vietnamese mobile phone numbers."""
    if not phone:
        return True, ""                         # phone is optional
    cleaned = re.sub(r'[\s\-]', '', phone)      # strip spaces/dashes
    if not re.match(r'^\+?[0-9]+$', cleaned):
        return False, "Số điện thoại chỉ được chứa chữ số (có thể có dấu + ở đầu)."
    # Normalise +84 → 0
    if cleaned.startswith('+84'):
        cleaned = '0' + cleaned[3:]
    elif cleaned.startswith('84') and len(cleaned) == 11:
        cleaned = '0' + cleaned[2:]
    if len(cleaned) != 10:
        return False, "Số điện thoại Việt Nam phải có đúng 10 chữ số."
    valid_prefixes = ('03', '05', '07', '08', '09')
    if not cleaned.startswith(valid_prefixes):
        return False, "Đầu số không hợp lệ. Đầu số hợp lệ: 03x, 05x, 07x, 08x, 09x."
    return True, cleaned


def validate_email(email: str):
    """Basic email syntax + domain check."""
    email = (email or '').strip().lower()
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Email không đúng định dạng. Ví dụ: abc@gmail.com"
    domain = email.split('@')[1]
    # Basic domain check – must have at least one dot
    if '.' not in domain or domain.startswith('.') or domain.endswith('.'):
        return False, "Tên miền email không hợp lệ."
    return True, email

# ─────────────────────────── Page Routes ───────────────────────────

@bp.route('/profile')
@login_required
def profile():
    """Trang Hồ sơ cá nhân – hiển thị thông tin."""
    return render_template('profile/index.html',
                           user=current_user,
                           active='profile')


@bp.route('/profile/activity')
@login_required
def activity():
    """Trang Quản lý hoạt động – xem/xoá bài đã đăng."""
    my_items = Item.query.filter_by(user_id=current_user.id) \
                         .order_by(Item.date_posted.desc()).all()
    lost_items  = [i for i in my_items if i.item_type == 'Lost']
    found_items = [i for i in my_items if i.item_type == 'Found']
    return render_template('profile/activity.html',
                           user=current_user,
                           lost_items=lost_items,
                           found_items=found_items,
                           active='activity')


@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Trang Cập nhật thông tin cá nhân (full_name, email, phone, avatar, about)."""
    if request.method == 'POST':
        full_name  = (request.form.get('full_name') or '').strip()
        email      = (request.form.get('email') or '').strip()
        phone      = (request.form.get('phone') or '').strip()
        about      = (request.form.get('about') or '').strip()
        avatar_url = (request.form.get('avatar_url') or '').strip()

        # Handle file upload for avatar
        avatar_file = request.files.get('avatar_file')
        if avatar_file and avatar_file.filename:
            from werkzeug.utils import secure_filename
            import os
            from flask import current_app
            filename = secure_filename(avatar_file.filename)
            # Create uploads directory if it doesn't exist
            uploads_dir = os.path.join(current_app.root_path, '../frontend/static/uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            # Add dynamic timestamp to avoid browser caching issues with same name
            import time
            save_name = f"{int(time.time())}_{filename}"
            filepath = os.path.join(uploads_dir, save_name)
            avatar_file.save(filepath)
            # Update user's avatar_url to the newly uploaded file path
            avatar_url = url_for('static', filename='uploads/' + save_name)

        # --- Validate email ---
        ok, result = validate_email(email)
        if not ok:
            flash(result, 'danger')
            return redirect(url_for('profile.edit_profile'))

        # Check email uniqueness (exclude self)
        from app.models.user import User
        existing = User.query.filter(User.email == result,
                                     User.id != current_user.id).first()
        if existing:
            flash('Email này đã được dùng bởi tài khoản khác.', 'danger')
            return redirect(url_for('profile.edit_profile'))

        # --- Validate phone ---
        ok, result_phone = validate_phone(phone)
        if not ok:
            flash(result_phone, 'danger')
            return redirect(url_for('profile.edit_profile'))

        # --- Persist ---
        current_user.full_name   = full_name
        current_user.email       = result          # normalised email
        current_user.phone_number = result_phone if result_phone else phone
        current_user.about_me    = about
        if avatar_url:
            current_user.avatar_url = avatar_url
        db.session.commit()

        flash('Cập nhật hồ sơ thành công!', 'success')
        return redirect(url_for('profile.profile'))

    return render_template('profile/edit.html',
                           user=current_user,
                           active='edit')


@bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Trang Đổi mật khẩu."""
    if request.method == 'POST':
        old_pass  = request.form.get('old_password', '')
        new_pass  = request.form.get('new_password', '')
        conf_pass = request.form.get('confirm_password', '')

        if not current_user.check_password(old_pass):
            flash('Mật khẩu hiện tại không đúng!', 'danger')
            return redirect(url_for('profile.change_password'))

        if len(new_pass) < 6:
            flash('Mật khẩu mới phải có ít nhất 6 ký tự.', 'danger')
            return redirect(url_for('profile.change_password'))

        if new_pass != conf_pass:
            flash('Xác nhận mật khẩu không khớp.', 'danger')
            return redirect(url_for('profile.change_password'))

        current_user.set_password(new_pass)
        db.session.commit()
        flash('Đổi mật khẩu thành công!', 'success')
        return redirect(url_for('profile.profile'))

    return render_template('profile/password.html',
                           user=current_user,
                           active='password')


# ─────────────────── Static / Informational Pages ──────────────────

@bp.route('/about')
def about():
    return render_template('profile/about.html', active='about')


@bp.route('/guide')
def guide():
    return render_template('profile/guide.html', active='guide')
