from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from collections import defaultdict
import os
from app.extensions import db, socketio
from app.core.decorators import admin_required
from app.models.user import User
from app.models.item import Item
from app.models.action_log import ActionLog

bp = Blueprint('admin_dashboard', __name__)

@bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Statistics for Cards
    total_users = User.query.count()
    # New users today (VN Time 00:00)
    vn_now = datetime.utcnow() + timedelta(hours=7)
    vn_today_start = vn_now.replace(hour=0, minute=0, second=0, microsecond=0)
    utc_today_start = vn_today_start - timedelta(hours=7)
    new_users_today = User.query.filter(User.created_at >= utc_today_start).count()
    
    total_items = Item.query.count()
    total_lost = Item.query.filter_by(item_type='Lost').count()
    total_found = Item.query.filter_by(item_type='Found').count()
    
    # Success match: Items that are Closed
    success_matches = Item.query.filter_by(status='Closed').count()
    success_rate = (success_matches / total_items * 100) if total_items > 0 else 0

    # DB Health
    db_size = 0
    try:
        db_path = os.path.join('backend', 'instance', 'flostfound.db')
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / 1024
    except:
        pass
    
    # Charts logic: 7 days
    dates = defaultdict(lambda: {'lost': 0, 'found': 0})
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    items = Item.query.filter(Item.date_posted >= seven_days_ago).all()
    
    for item in items:
        date_str = item.date_posted.strftime('%Y-%m-%d')
        if item.item_type == 'Lost':
            dates[date_str]['lost'] += 1
        else:
            dates[date_str]['found'] += 1
            
    sorted_dates = sorted(dates.keys())
    chart_labels = sorted_dates if sorted_dates else [datetime.utcnow().strftime('%Y-%m-%d')]
    chart_lost_data = [dates[d]['lost'] for d in chart_labels]
    chart_found_data = [dates[d]['found'] for d in chart_labels]
    
    # Hotspot locations
    location_data = db.session.query(Item.location, db.func.count(Item.id)).group_by(Item.location).order_by(db.func.count(Item.id).desc()).limit(5).all()

    return render_template('admin/dashboard.html', 
                           total_users=total_users, 
                           new_users_today=new_users_today,
                           total_items=total_items,
                           total_lost=total_lost,
                           total_found=total_found,
                           success_matches=success_matches,
                           success_rate=success_rate,
                           db_size=f"{db_size:.1f} KB",
                           chart_labels=chart_labels,
                           chart_lost_data=chart_lost_data,
                           chart_found_data=chart_found_data,
                           hotspots=location_data,
                           now=datetime.utcnow() + timedelta(hours=7),
                           timedelta=timedelta)

@bp.route('/admin/users')
@login_required
@admin_required
def admin_users():
    search_query = request.args.get('q', '')
    role_filter = request.args.get('role', '') # 'admin', 'banned', 'user'
    
    query = User.query
    if search_query:
        query = query.filter((User.username.contains(search_query)) | (User.email.contains(search_query)))
    
    if role_filter == 'admin':
        query = query.filter(User.level == 1)
    elif role_filter == 'banned':
        query = query.filter_by(is_banned=True)
    
    users = query.order_by(User.level.asc(), User.id.desc()).all()
    # Apply timezone +7 in route to avoid Jinja issues
    for u in users:
        if u.last_seen:
            u.local_last_seen = u.last_seen + timedelta(hours=7)
        if u.ban_until:
            u.local_ban_until = u.ban_until + timedelta(hours=7)
            
    return render_template('admin/users.html', users=users, search_query=search_query, role_filter=role_filter, now=datetime.utcnow() + timedelta(hours=7), timedelta=timedelta)

@bp.route('/admin/users/ban/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def ban_user(user_id):
    user = User.query.get_or_404(user_id)
    # Permission check: current_user.level must be lower than user_to_ban.level (e.g. 1 can ban 3, but 2 cannot ban 1).
    if current_user.level != 1:
        flash("Bạn không có quyền ban người dùng!", "danger")
        return redirect(url_for('admin_dashboard.admin_users'))
        
    duration = request.form.get('duration') # '1', '7', 'permanent'
    if duration == '1':
        user.ban_until = datetime.utcnow() + timedelta(days=1)
    elif duration == '7':
        user.ban_until = datetime.utcnow() + timedelta(days=7)
    else:
        user.ban_until = None # Permanent
        
    user.is_banned = True
    
    # Log action
    log = ActionLog(user_id=current_user.id, action="Khóa tài khoản", details=f"User: {user.username}, Duration: {duration}")
    db.session.add(log)
    db.session.commit()
    
    flash(f"Đã khóa tài khoản {user.username}.", "success")
    return redirect(url_for('admin_dashboard.admin_users'))

@bp.route('/admin/users/unban/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def unban_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    user.ban_until = None
    
    log = ActionLog(user_id=current_user.id, action="Mở khóa tài khoản", details=f"User: {user.username}")
    db.session.add(log)
    db.session.commit()
    
    flash(f"Đã mở khóa tài khoản {user.username}.", "success")
    return redirect(url_for('admin_dashboard.admin_users'))

@bp.route('/admin/users/update_role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    user = User.query.get_or_404(user_id)
    
    # Permission check: Cannot update same level or higher
    if current_user.level >= user.level:
        flash("Bạn không có quyền thay đổi cấp độ của người cùng cấp hoặc cấp cao hơn!", "danger")
        return redirect(url_for('admin_dashboard.admin_users'))
        
    new_level = request.form.get('level', type=int)
    
    if new_level == 1:
        # Prevent demoting self or promoting others to level 1 easily via UI
        flash("Không thể thiết lập quyền Cấp 1 qua giao diện.", "warning")
    elif new_level == 3:
        user.level = 3
        user.is_admin = False
        flash(f"Đã gỡ quyền quản trị của {user.username} (về Cấp 3).", "success")
    
    db.session.commit()
    return redirect(url_for('admin_dashboard.admin_users'))

@bp.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.level >= user.level:
        flash("Bạn không có quyền xóa người cùng cấp hoặc cấp cao hơn!", "danger")
        return redirect(url_for('admin_dashboard.admin_users'))
    
    username = user.username
    
    # FIX: Manually delete related data to avoid IntegrityError (NOT NULL constraints)
    from app.models.message import Message
    from app.models.item import Item
    
    # 1. Delete all messages
    Message.query.filter((Message.sender_id == user_id) | (Message.recipient_id == user_id)).delete()
    
    # 2. Delete all items
    Item.query.filter_by(user_id=user_id).delete()
    
    # 3. Delete all action logs related to this user (as performer)
    ActionLog.query.filter_by(user_id=user_id).delete()
    
    # 4. Log action (This log is by CURRENT ADMIN, so it's safe)
    log = ActionLog(user_id=current_user.id, action="Xóa tài khoản vĩnh viễn", details=f"User: {username}, Email: {user.email}")
    
    # 5. Final delete user
    db.session.delete(user)
    db.session.add(log)
    db.session.commit()
    
    flash(f"Đã xóa vĩnh viễn tài khoản {username} và tất cả dữ liệu liên quan.", "success")
    return redirect(url_for('admin_dashboard.admin_users'))

@bp.route('/admin/users/create', methods=['POST'])
@login_required
@admin_required
def create_user():
    # Only Level 1/2 can create users. Level 2 can only create Level 3 users.
    target_level = request.form.get('level', type=int, default=3)
    
    if current_user.level == 2 and target_level <= 2:
        flash("Moderator chỉ có quyền tạo người dùng thông thường (Cấp 3).", "danger")
        return redirect(url_for('admin_dashboard.admin_users'))
        
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    level = request.form.get('level', type=int, default=3)
    
    if User.query.filter_by(username=username).first():
        flash("Tên đăng nhập đã tồn tại.", "danger")
    elif User.query.filter_by(email=email).first():
        flash("Email đã tồn tại.", "danger")
    else:
        new_user = User(username=username, email=email, level=3) # Force new created users to level 3
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash(f"Đã tạo thành công tài khoản {username}.", "success")
        
    return redirect(url_for('admin_dashboard.admin_users'))

@bp.route('/admin/broadcast', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_broadcast():
    if request.method == 'POST':
        message_text = request.form.get('message')
        if message_text:
            # 1. Phát qua Socket.IO (Hiện Toast tức thì)
            socketio.emit('announcement', {'message': message_text})
            
            # 2. Lưu vào tin nhắn chat của TẤT CẢ người dùng (ngoại trừ chính Admin)
            from app.models.message import Message
            users = User.query.filter(User.id != current_user.id).all()
            
            for user in users:
                new_msg = Message(
                    sender_id=current_user.id,
                    recipient_id=user.id,
                    body=f"📢 [THÔNG BÁO HỆ THỐNG]: {message_text}"
                )
                db.session.add(new_msg)
            
            # 3. Log hành động Admin
            log = ActionLog(user_id=current_user.id, action="Phát thông báo", details=message_text)
            db.session.add(log)
            db.session.commit()
            
            flash("Thông báo đã được gửi và lưu vào hộp thư của mọi người!", "success")
            
    return render_template('admin/broadcast.html')
