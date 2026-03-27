from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Item, Message, ActionLog
from ai_service import ai_detector
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flostfound.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 600
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['REMEMBER_COOKIE_DURATION'] = 600

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
socketio = SocketIO(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def refresh_ai_model():
    with app.app_context():
        # Get all posts text for AI training
        items = Item.query.all()
        texts = [f"{item.title} {item.description}" for item in items]
        ai_detector.fit_data(texts)

from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (current_user.level > 2 and not current_user.is_admin):
            flash('Bạn không có quyền truy cập trang này.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        # Get private messages
        unread_messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.timestamp.desc()).limit(10).all()
        
        # Get system logs (actions)
        system_logs = ActionLog.query.filter_by(user_id=current_user.id).order_by(ActionLog.timestamp.desc()).limit(10).all()
        
        all_notifications = []
        
        # Convert Messages
        for msg in unread_messages:
            all_notifications.append({
                'type': 'message',
                'sender_name': msg.sender.username,
                'sender_initial': msg.sender.username[0].upper(),
                'body': msg.body,
                'timestamp': msg.timestamp
            })
            
        # Convert Logs
        for log in system_logs:
            all_notifications.append({
                'type': 'log',
                'sender_name': 'Hệ thống',
                'sender_initial': 'H',
                'body': f"{log.action}: {log.details}" if log.details else log.action,
                'timestamp': log.timestamp
            })
            
        # Sort by timestamp descending
        all_notifications.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit total
        final_notifications = all_notifications[:10]
        
        return dict(notifications=final_notifications, notification_count=len(final_notifications))
    return dict(notifications=[], notification_count=0)

@app.route('/')
def index():
    query = request.args.get('q', '').strip()
    if query:
        items = Item.query.filter(
            (Item.title.contains(query)) | 
            (Item.description.contains(query)) |
            (Item.location.contains(query))
        ).order_by(Item.date_posted.desc()).all()
    else:
        items = Item.query.order_by(Item.date_posted.desc()).all()
    return render_template('index.html', items=items, query=query)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Tên đăng nhập đã tồn tại.', 'danger')
            return redirect(url_for('register'))
            
        new_user = User(username=username, email=email, level=3)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Tạo tài khoản thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('index'))
        else:
            flash('Đăng nhập thất bại. Kiểm tra lại thông tin.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/post', methods=['GET', 'POST'])
@login_required
def post_item():
    if request.method == 'POST':
        # Check if AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.best == 'application/json'

        title = request.form.get('title')
        desc = request.form.get('description')
        location = request.form.get('location')
        specific_location = request.form.get('specific_location')
        category = request.form.get('category')
        itype = request.form.get('item_type')
        phone_number = request.form.get('phone_number')
        facebook_url = request.form.get('facebook_url')
        incident_date_str = request.form.get('incident_date')
        
        # Backward compatibility for contact_info column
        contact = f"SĐT: {phone_number}"
        if facebook_url:
            contact += f" | FB: {facebook_url}"

        incident_date = None
        if incident_date_str:
            try:
                incident_date = datetime.strptime(incident_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    incident_date = datetime.strptime(incident_date_str, '%Y-%m-%d')
                except ValueError:
                    pass
        
        # AI Spam Check (Optional fallback if ai_detector not loaded)
        try:
            post_text = f"{title} {desc}"
            is_spam, score = ai_detector.is_spam(post_text)
            if is_spam:
                msg = f'Bài viết bị từ chối: Nội dung quá giống với bài viết đã có (Độ trùng lặp: {score:.2f}).'
                if is_ajax: return jsonify({'success': False, 'message': msg})
                flash(msg, 'warning')
                return redirect(url_for('index'))
        except:
            pass

        new_item = Item(
            title=title, description=desc, location=location, 
            item_type=itype, contact_info=contact, user_id=current_user.id,
            phone_number=phone_number, facebook_url=facebook_url,
            category=category, incident_date=incident_date
        )
        db.session.add(new_item)
        db.session.commit()
        
        # Handle Image Uploads
        uploaded_files = request.files.getlist('images')
        saved_image_urls = []
        
        # Try Cloudinary first
        cloudinary_url = os.environ.get('CLOUDINARY_URL')
        
        for file in uploaded_files:
            if file and file.filename != '':
                try:
                    if cloudinary_url:
                        import cloudinary.uploader
                        upload_result = cloudinary.uploader.upload(file, folder="flostfound/posts")
                        url = upload_result.get('secure_url')
                    else:
                        # Local upload
                        from werkzeug.utils import secure_filename
                        filename = secure_filename(f"post_{new_item.id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
                        upload_path = os.path.join(app.root_path, 'static', 'uploads')
                        if not os.path.exists(upload_path): os.makedirs(upload_path)
                        file.save(os.path.join(upload_path, filename))
                        url = f"/static/uploads/{filename}"
                    
                    saved_image_urls.append(url)
                except Exception as e:
                    print(f"Upload error: {e}")

        # Set primary image and update DB
        if saved_image_urls:
            new_item.image_url = saved_image_urls[0]
            # If you have an ItemImage table in the root models.py, add them there too.
            # Root models.py doesn't seem to have ItemImage table yet. 
            # I'll check if it exists before adding.
            db.session.commit()
        
        # Log action
        log = ActionLog(user_id=current_user.id, action="Đăng bài", details=f"Tiêu đề: {title}")
        db.session.add(log)
        db.session.commit()
        
        # Update AI model
        try:
            refresh_ai_model()
        except:
            pass
        
        if is_ajax:
            return jsonify({'success': True, 'item_id': new_item.id, 'redirect_url': url_for('index')})
            
        flash('Đăng tin thành công!', 'success')
        return redirect(url_for('index'))
        
    return render_template('post_item.html')

@app.route('/chat/<int:recipient_id>')
@login_required
def chat(recipient_id):
    recipient = User.query.get_or_404(recipient_id)
    # Get history
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == recipient_id)) |
        ((Message.sender_id == recipient_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()
    
    return render_template('chat.html', recipient=recipient, messages=messages, datetime=datetime)

@app.route('/messages')
@login_required
def messages_inbox():
    # Find all users involved in conversations with current_user
    # distinct sender_id where recipient = current
    # distinct recipient_id where sender = current
    
    # Simple approach: Get all messages involving current_user, order by time desc
    all_msgs = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.timestamp.desc()).all()
    
    conversations = {}
    for msg in all_msgs:
        other_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id
        if other_id not in conversations:
            other_user = User.query.get(other_id)
            if other_user:
                conversations[other_id] = {
                    'user': other_user,
                    'last_message': msg
                }
    
    # Convert to list
    inbox_items = list(conversations.values())
    return render_template('inbox.html', conversations=inbox_items)

@socketio.on('join_notifications')
def on_join_notifications():
    if current_user.is_authenticated:
        room = f"user_{current_user.id}"
        join_room(room)

@socketio.on('send_message')
def handle_message(data):
    # data = {recipient_id, message}
    recipient_id = data.get('recipient_id')
    body = data.get('message')
    
    if not current_user.is_authenticated:
        return
        
    msg = Message(sender_id=current_user.id, recipient_id=recipient_id, body=body)
    db.session.add(msg)
    db.session.commit()
    
    room = f"chat_{min(current_user.id, int(recipient_id))}_{max(current_user.id, int(recipient_id))}"
    emit('receive_message', {
        'sender_id': current_user.id,
        'message': body,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M')
    }, room=room)
    
    # Emit notification to recipient's private room
    notification_room = f"user_{recipient_id}"
    emit('notification', {
        'sender_id': current_user.id,
        'sender_name': current_user.username,
        'message': body
    }, room=notification_room)

@socketio.on('join_chat')
def on_join(data):
    recipient_id = data.get('recipient_id')
    room = f"chat_{min(current_user.id, int(recipient_id))}_{max(current_user.id, int(recipient_id))}"
    join_room(room)

# ==========================================
# WebRTC SIGNALING LOGIC (Video/Voice Call)
# ==========================================

@socketio.on('call_user')
def on_call_user(data):
    """ Người A gửi yêu cầu gọi (Offer) cho người B """
    if not current_user.is_authenticated: return
    
    user_to_call = data.get('user_to_call')
    signal_data = data.get('signal_data')
    is_video = data.get('is_video', True)
    
    room = f"user_{user_to_call}"
    emit('call_made', {
        'signal': signal_data,
        'from': current_user.id,
        'from_name': current_user.username,
        'from_avatar': current_user.avatar,
        'is_video': is_video
    }, room=room)

@socketio.on('user_busy')
def on_user_busy(data):
    """ Người B phản hồi lại là đang bận cuộc gọi khác """
    if not current_user.is_authenticated: return
    to_user = data.get('to')
    room = f"user_{to_user}"
    emit('call_busy', {'from': current_user.id}, room=room)

@socketio.on('make_answer')
def on_make_answer(data):
    """ Người B chấp nhận và gửi Phản hồi (Answer) lại cho A """
    if not current_user.is_authenticated: return
    
    to_user = data.get('to')
    signal_data = data.get('signal')
    
    room = f"user_{to_user}"
    emit('answer_made', {
        'signal': signal_data,
        'to': current_user.id
    }, room=room)

@socketio.on('ice_candidate')
def on_ice_candidate(data):
    """ Trung chuyển thông tin mạng ICE Candidate cho 2 máy kết nối P2P """
    if not current_user.is_authenticated: return
    
    to_user = data.get('to')
    candidate = data.get('candidate')
    
    room = f"user_{to_user}"
    emit('ice_candidate', {
        'candidate': candidate,
        'from': current_user.id
    }, room=room)

@socketio.on('reject_call')
def on_reject_call(data):
    """ Xử lý khi người B Ấn nút Từ Chối """
    if not current_user.is_authenticated: return
    
    to_user = data.get('to')
    room = f"user_{to_user}"
    
    # Save call log
    msg = Message(sender_id=current_user.id, recipient_id=to_user, body="📞 Cuộc gọi bị từ chối")
    db.session.add(msg)
    db.session.commit()
    
    emit('call_rejected', {
        'from': current_user.id
    }, room=room)

@socketio.on('end_call')
def on_end_call(data):
    """ Xử lý khi đang gọi mà Cúp máy """
    if not current_user.is_authenticated: return
    
    to_user = data.get('to')
    duration = data.get('duration', 0)
    
    if duration == 0:
        body = "📞 Cuộc gọi nhỡ"
    else:
        m, s = divmod(duration, 60)
        body = f"📞 Cuộc gọi video kết thúc - {m:02d}:{s:02d}"
        
    msg = Message(sender_id=current_user.id, recipient_id=to_user, body=body)
    db.session.add(msg)
    db.session.commit()
    
    room = f"user_{to_user}"
    emit('call_ended', {
        'from': current_user.id
    }, room=room)

# Admin Routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # User Management Search
    search_query = request.args.get('q', '')
    if search_query:
        users = User.query.filter(
            (User.username.contains(search_query)) | 
            (User.email.contains(search_query))
        ).all()
    else:
        users = User.query.order_by(User.last_seen.desc()).all()

    # Statistics
    total_users = User.query.count()
    total_items = Item.query.count()
    total_lost = Item.query.filter_by(item_type='Lost').count()
    total_found = Item.query.filter_by(item_type='Found').count()
    
    # Calculate stats for charts
    lost_items = Item.query.filter_by(item_type='Lost').all()
    found_items = Item.query.filter_by(item_type='Found').all()
    
    # Helper to count items by date
    from collections import defaultdict
    dates = defaultdict(lambda: {'lost': 0, 'found': 0})
    
    for item in lost_items:
        date_str = item.date_posted.strftime('%Y-%m-%d')
        dates[date_str]['lost'] += 1
        
    for item in found_items:
        date_str = item.date_posted.strftime('%Y-%m-%d')
        dates[date_str]['found'] += 1
        
    # Sort dates
    sorted_dates = sorted(dates.keys())
    chart_labels = sorted_dates[-7:] # Last 7 days
    chart_lost_data = [dates[d]['lost'] for d in chart_labels]
    chart_found_data = [dates[d]['found'] for d in chart_labels]
    
    return render_template('admin_dashboard.html', 
                           total_users=total_users, 
                           total_items=total_items,
                           total_lost=total_lost,
                           total_found=total_found,
                           chart_labels=chart_labels,
                           chart_lost_data=chart_lost_data,
                           chart_found_data=chart_found_data,
                           users=users,
                           search_query=search_query,
                           now=datetime.utcnow())

@app.route('/admin/posts')
@login_required
@admin_required
def admin_posts():
    items = Item.query.order_by(Item.date_posted.desc()).all()
    return render_template('admin_posts.html', items=items)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    search_query = request.args.get('q', '')
    role_filter = request.args.get('role', '')
    
    query = User.query
    if search_query:
        query = query.filter((User.username.contains(search_query)) | (User.email.contains(search_query)))
    
    if role_filter == 'admin':
        query = query.filter(User.level <= 2)
    elif role_filter == 'banned':
        query = query.filter(User.is_banned == True)
        
    users = query.order_by(User.level.asc(), User.username.asc()).all()
    return render_template('admin/users.html', users=users, search_query=search_query, role_filter=role_filter, now=datetime.utcnow())

@app.route('/admin/users/promote/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def promote_user(user_id):
    if current_user.level != 1:
        flash('Chỉ Admin Cấp 1 mới có quyền thăng cấp.', 'danger')
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(user_id)
    if user.level > 2:
        user.level = 2
        user.is_admin = True
        db.session.commit()
        flash(f'Đã thăng cấp {user.username} lên Moderator (Cấp 2).', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/ban/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def ban_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Permission check: Level 1 can ban any level > 1. Level 2 can only ban level 3.
    if current_user.level >= user.level:
        flash('Bạn không có quyền ban người cùng cấp hoặc cấp cao hơn.', 'danger')
        return redirect(url_for('admin_users'))
    
    duration = request.form.get('duration')
    user.is_banned = True
    if duration == 'permanent':
        user.ban_until = None
    else:
        from datetime import timedelta
        days = int(duration) if duration.isdigit() else 1
        user.ban_until = datetime.utcnow() + timedelta(days=days)
    
    db.session.commit()
    flash(f'Đã ban người dùng {user.username}.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/unban/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def unban_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.level >= user.level and user.level != 3:
        # Super admin can unban moderators, but moderator cannot unban super admin (won't happen as they can't be banned)
        pass 

    user.is_banned = False
    user.ban_until = None
    db.session.commit()
    flash(f'Đã bỏ ban người dùng {user.username}.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def force_delete_user(user_id):
    from app.models.comment import Comment
    from app.models.like import Like
    from app.models.message import Message
    from app.models.notification import Notification
    from app.models.user_preference import MutedItem, BlockedUser
    from app.models.item import Item
    from app.models.report import Report
    
    user = User.query.get_or_404(user_id)
    
    if current_user.level >= user.level:
        flash('Bạn không có quyền xóa người cùng cấp hoặc cấp cao hơn.', 'danger')
        return redirect(url_for('admin_users'))
    
    username = user.username
    
    try:
        # Delete all related data in order of dependencies
        Comment.query.filter_by(user_id=user_id).delete()
        Like.query.filter_by(user_id=user_id).delete()
        Message.query.filter((Message.sender_id == user_id) | (Message.recipient_id == user_id)).delete()
        Notification.query.filter((Notification.recipient_id == user_id) | (Notification.actor_id == user_id)).delete()
        MutedItem.query.filter_by(user_id=user_id).delete()
        BlockedUser.query.filter((BlockedUser.user_id == user_id) | (BlockedUser.blocked_user_id == user_id)).delete()
        Report.query.filter_by(reporter_id=user_id).delete()
        Item.query.filter_by(user_id=user_id).delete()
        
        db.session.delete(user)
        db.session.commit()
        flash(f'Đã xóa vĩnh viễn tài khoản {username} và dữ liệu liên quan.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa tài khoản: {str(e)}', 'danger')
    
    return redirect(url_for('admin_users'))

# Static Pages
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not check_password_hash(current_user.password, current_password):
            flash('Mật khẩu hiện tại không đúng.', 'danger')
        elif new_password != confirm_password:
            flash('Mật khẩu mới không khớp.', 'danger')
        elif len(new_password) < 6:
            flash('Mật khẩu mới phải có ít nhất 6 ký tự.', 'danger')
        else:
            current_user.password = generate_password_hash(new_password, method='scrypt')
            db.session.commit()
            flash('Đổi mật khẩu thành công!', 'success')
            return redirect(url_for('profile'))
            
    return render_template('change_password.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Handle Avatar Upload
        if 'avatar_file' in request.files: # Match the field name in edit.html
            file = request.files['avatar_file']
            if file and file.filename != '' and '.' in file.filename:
                # Check extension
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                if file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    from werkzeug.utils import secure_filename
                    import os
                    
                    filename = secure_filename(f"user_{current_user.id}_{int(datetime.utcnow().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}")
                    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    
                    file.save(os.path.join(upload_folder, filename))
                    current_user.avatar_url = filename
                    
                    # Log Avatar Update
                    log = ActionLog(user_id=current_user.id, action="Cập nhật", details="Thay đổi ảnh đại diện")
                    db.session.add(log)
        
        # Also check for manual avatar_url
        new_avatar_url = request.form.get('avatar_url')
        if new_avatar_url:
            current_user.avatar_url = new_avatar_url

        # Update Profile Info
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        about = request.form.get('about')
        
        if email:
            # Check unique email
            existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
            if existing_user:
                flash('Email này đã được sử dụng bởi tài khoản khác.', 'danger')
            else:
                current_user.email = email

        if full_name:
            current_user.full_name = full_name
        
        if phone:
            current_user.phone = phone
            
        if about:
            current_user.about_me = about
        
        db.session.commit()
        flash('Cập nhật thông tin thành công!', 'success')
        return redirect(url_for('profile'))
        
    # Get user's items
    my_items = Item.query.filter_by(user_id=current_user.id).order_by(Item.date_posted.desc()).all()
    lost_items = [i for i in my_items if i.item_type == 'Lost']
    found_items = [i for i in my_items if i.item_type == 'Found']
    
    return render_template('profile.html', user=current_user)

# Unified delete route for Admin and Post Owner
@app.route('/post/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_post(item_id):
    item = Item.query.get_or_404(item_id)
    
    # Check permission: Super Admin (1), Moderator (2) or Owner
    is_authorized = (current_user.id == item.user_id)
    if current_user.level == 1:
        is_authorized = True
    elif current_user.level == 2:
        # Moderator can delete posts of Level 3 users or their own
        if item.user.level > 2 or item.user_id == current_user.id:
            is_authorized = True
            
    if not is_authorized:
        flash('Bạn không có quyền xóa bài này.', 'danger')
        return redirect(url_for('index'))
        
    # Log the deletion
    action_type = "Admin Xóa bài" if current_user.is_admin and current_user.id != item.user_id else "Người dùng xóa bài"
    log = ActionLog(user_id=current_user.id, action=action_type, details=f"Đã xóa bài: {item.title}")
    db.session.add(log)
    
    db.session.delete(item)
    db.session.commit()
    flash('Đã xóa bài đăng.', 'success')
    
    # Redirect back to where they came from if possible, or default
    if request.referrer and 'admin' in request.referrer:
        return redirect(url_for('admin_posts'))
    elif request.referrer and 'profile' in request.referrer:
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('index'))

@app.route('/my-posts')
@login_required
def my_posts():
    # Get user's items
    my_items = Item.query.filter_by(user_id=current_user.id).order_by(Item.date_posted.desc()).all()
    lost_items = [i for i in my_items if i.item_type == 'Lost']
    found_items = [i for i in my_items if i.item_type == 'Found']
    
    return render_template('my_posts.html', user=current_user, lost_items=lost_items, found_items=found_items)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # FIX: Force add missing columns
        from sqlalchemy import text
        try:
            db.session.execute(text("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
            db.session.execute(text("ALTER TABLE user ADD COLUMN level INTEGER DEFAULT 3"))
            db.session.execute(text("ALTER TABLE user ADD COLUMN is_banned BOOLEAN DEFAULT 0"))
            db.session.execute(text("ALTER TABLE user ADD COLUMN ban_until DATETIME"))
            db.session.execute(text("ALTER TABLE user ADD COLUMN trust_score INTEGER DEFAULT 100"))
            db.session.execute(text("ALTER TABLE user ADD COLUMN last_seen DATETIME"))
            db.session.execute(text("ALTER TABLE item ADD COLUMN status VARCHAR(20) DEFAULT 'Open'"))
            db.session.commit()
            print("Successfully migrated columns in root DB!")
        except Exception:
            db.session.rollback()

        # FORCE ADMIN
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Creating default admin account...")
            admin = User(username='admin', email='admin@fpt.edu.vn', is_admin=True, level=1)
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
            print("Admin account created (root).")
        else:
            admin.is_admin = True
            admin.level = 1
            admin.set_password('123456')
            db.session.commit()
            print("Admin account updated (root).")

        refresh_ai_model()
    socketio.run(app, debug=True, use_reloader=True, log_output=True)
