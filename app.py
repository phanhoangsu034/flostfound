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
app.config['SECRET_KEY'] = 'dev_key_secret' # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flostfound.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
        if not current_user.is_authenticated or not current_user.is_admin:
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
            
        new_user = User(username=username, email=email, password=generate_password_hash(password, method='scrypt'))
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
            login_user(user)
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
        title = request.form.get('title')
        desc = request.form.get('description')
        location = request.form.get('location')
        itype = request.form.get('item_type')
        contact = request.form.get('contact_info')
        
        # AI Spam Check
        post_text = f"{title} {desc}"
        is_spam, score = ai_detector.is_spam(post_text)
        
        if is_spam:
            flash(f'Bài viết bị từ chối: Nội dung quá giống với bài viết đã có (Độ trùng lặp: {score:.2f}). Vui lòng kiểm tra xem bạn đã đăng chưa.', 'warning')
            return render_template('post_item.html', title=title, description=desc, location=location, contact_info=contact)

        new_item = Item(
            title=title, description=desc, location=location, 
            item_type=itype, contact_info=contact, user_id=current_user.id
        )
        db.session.add(new_item)
        db.session.commit()
        
        # Log action
        log = ActionLog(user_id=current_user.id, action="Đăng bài", details=f"Tiêu đề: {title}")
        db.session.add(log)
        db.session.commit()
        
        # Update AI model with new data
        refresh_ai_model()
        
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

# ... existing admin routes ...

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
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '':
                from werkzeug.utils import secure_filename
                import os
                
                # Check extension
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    filename = secure_filename(f"user_{current_user.id}_{int(datetime.utcnow().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}")
                    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    
                    file.save(os.path.join(upload_folder, filename))
                    current_user.avatar = filename
                    db.session.commit()
                    flash('Cập nhật ảnh đại diện thành công!', 'success')
                    
                    # Log Avatar Update
                    log = ActionLog(user_id=current_user.id, action="Cập nhật", details="Thay đổi ảnh đại diện")
                    db.session.add(log)
                    db.session.commit()
                else:
                    flash('Định dạng ảnh không hỗ trợ. Chỉ chấp nhận png, jpg, jpeg, gif.', 'danger')
            return redirect(url_for('profile'))

        # Update Profile Info (Only if not Avatar Upload)
        phone = request.form.get('phone')
        email = request.form.get('email')
        
        # Validation Patterns
        import re
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('Email không hợp lệ. Vui lòng kiểm tra lại (VD: user@example.com).', 'danger')
            return redirect(url_for('profile'))
        
        # Phone: Starts with 0 (10 digits) or +84 (11 digits), prefix 3,5,7,8,9
        if phone and not re.match(r'^(0|\+84)[35789][0-9]{8}$', phone):
            flash('Số điện thoại không hợp lệ.', 'danger')
            return redirect(url_for('profile'))
        
        # Check if email/phone already exists (excluding current user)
        existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_user:
            flash('Email này đã được sử dụng bởi tài khoản khác.', 'danger')
            return redirect(url_for('profile'))

        # Update Username
        new_username = request.form.get('username')
        if new_username and new_username != current_user.username:
            # Check if username exists
            existing_username = User.query.filter(User.username == new_username).first()
            if existing_username:
                flash('Tên hiển thị này đã được sử dụng. Vui lòng chọn tên khác.', 'danger')
                return redirect(url_for('profile'))
            current_user.username = new_username
            
            # Log Username Update
            log = ActionLog(user_id=current_user.id, action="Cập nhật", details=f"Đổi tên thành {new_username}")
            db.session.add(log)

        current_user.phone = phone
        current_user.email = email
        
        # Log Profile Update
        log = ActionLog(user_id=current_user.id, action="Cập nhật", details="Thay đổi thông tin cá nhân")
        db.session.add(log)
        
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
    
    # Check permission: Admin or Owner
    if not current_user.is_admin and current_user.id != item.user_id:
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
        refresh_ai_model()
    socketio.run(app, debug=True, use_reloader=True, log_output=True)
