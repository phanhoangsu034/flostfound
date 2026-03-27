"""
Posts interactions routes: Like, Comment & Tag API
"""
import re
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.item import Item
from app.models.like import Like
from app.models.comment import Comment
from app.models.user import User
from app.models.notification import Notification
from app.models.user_preference import BlockedUser, MutedUser
from datetime import datetime, timedelta

bp = Blueprint('posts_interactions', __name__)

def _apply_spam_penalty(user):
    """
    Apply incremental spam penalty:
    1 strike -> warning (no lock)
    2 strikes -> lock 10 mins
    3 strikes -> lock 24 hours
    4 strikes -> ban 3 days
    """
    now = datetime.utcnow()
    user.spam_strikes = (user.spam_strikes or 0) + 1
    
    if user.spam_strikes == 2:
        user.tagging_locked_until = now + timedelta(minutes=10)
    elif user.spam_strikes == 3:
        user.tagging_locked_until = now + timedelta(hours=24)
    elif user.spam_strikes >= 4:
        user.is_banned = True
        user.ban_until = now + timedelta(days=3)
        
    db.session.commit()

# ─── LIKE ───────────────────────────────────────────────

@bp.route('/api/posts/<int:item_id>/like', methods=['POST'])
@login_required
def toggle_like(item_id):
    """Toggle like on a post (like ↔ unlike)"""
    item = Item.query.get_or_404(item_id)
    existing = Like.query.filter_by(user_id=current_user.id, item_id=item_id).first()

    if existing:
        db.session.delete(existing)
        
        # Remove notification if unlike
        Notification.query.filter_by(
            action_type='like', actor_id=current_user.id, item_id=item_id
        ).delete()
        
        db.session.commit()
        liked = False
    else:
        new_like = Like(user_id=current_user.id, item_id=item_id)
        db.session.add(new_like)
        
        # Add Notification
        if current_user.id != item.user_id:
            notif = Notification(
                recipient_id=item.user_id,
                actor_id=current_user.id,
                item_id=item_id,
                action_type='like',
                content=f'{current_user.username} đã thích tin "{item.title}" của bạn'
            )
            db.session.add(notif)
            
            # Emit socket
            from app.extensions import socketio
            socketio.emit('notification', {
                'message': notif.content,
                'sender_name': 'Like mới',
                'type': 'new_notification'
            }, room=f'user_{item.user_id}')
            
        db.session.commit()
        liked = True

    return jsonify({
        'success': True,
        'liked': liked,
        'like_count': item.likes.count()
    })


@bp.route('/api/posts/<int:item_id>/like_status')
def get_like_status(item_id):
    """Get like status & count for a post"""
    item = Item.query.get_or_404(item_id)
    liked = False
    if current_user.is_authenticated:
        liked = Like.query.filter_by(user_id=current_user.id, item_id=item_id).first() is not None

    return jsonify({
        'success': True,
        'liked': liked,
        'like_count': item.likes.count()
    })


# ─── COMMENTS ───────────────────────────────────────────

@bp.route('/api/posts/<int:item_id>/comments')
def get_comments(item_id):
    """Get all comments for a post (flat list with parent_id for threading)"""
    item = Item.query.get_or_404(item_id)
    comments = Comment.query.filter_by(item_id=item_id).order_by(Comment.date_posted.asc()).all()

    return jsonify({
        'success': True,
        'comments': [c.to_dict() for c in comments],
        'comment_count': len(comments)
    })


@bp.route('/api/posts/<int:item_id>/comments', methods=['POST'])
@login_required
def add_comment(item_id):
    """Add a new comment to a post"""
    now = datetime.utcnow()
    
    # Pre-check for tagging/commenting ban
    if current_user.tagging_locked_until and current_user.tagging_locked_until > now:
        return jsonify({'success': False, 'message': 'Tài khoản của bạn đang bị khóa tính năng bình luận/tag do vi phạm spam/report.'}), 403

    item = Item.query.get_or_404(item_id)
    data = request.get_json()

    content = data.get('content', '').strip() if data else ''
    if not content:
        return jsonify({'success': False, 'message': 'Nội dung bình luận không được để trống'}), 400

    if len(content) > 500:
        return jsonify({'success': False, 'message': 'Bình luận tối đa 500 ký tự'}), 400
        
    mentioned_usernames = set(re.findall(r'@(\w+)', content))
    if len(mentioned_usernames) > 5:
        return jsonify({'success': False, 'message': 'Chỉ được tag tối đa 5 người trong 1 bình luận.'}), 400
        
    # --- Spam Detection ---
    recent_comments = Comment.query.filter_by(user_id=current_user.id).filter(
        Comment.date_posted >= now - timedelta(minutes=3)
    ).order_by(Comment.date_posted.desc()).all()
    
    # 1. Identical comment check (3 identical comments in 3 mins)
    identical_count = sum(1 for c in recent_comments if c.content == content)
    if identical_count >= 2:
        _apply_spam_penalty(current_user)
        return jsonify({'success': False, 'message': 'Phát hiện spam bình luận giống nhau! Tài khoản đang bị phạt.'}), 403
        
    # 2. Tag volume check (>= 20 tags in 1 min)
    if mentioned_usernames:
        recent_1min_comments = [c for c in recent_comments if c.date_posted >= now - timedelta(minutes=1)]
        tags_last_min = 0
        for rc in recent_1min_comments:
            tags_last_min += len(set(re.findall(r'@(\w+)', rc.content)))
        
        if tags_last_min + len(mentioned_usernames) >= 20:
            _apply_spam_penalty(current_user)
            return jsonify({'success': False, 'message': 'Hệ thống phát hiện spam tag. Tài khoản đang bị phạt.'}), 403

    comment = Comment(
        content=content,
        user_id=current_user.id,
        item_id=item_id,
        parent_id=data.get('parent_id') if data else None
    )
    db.session.add(comment)
    db.session.flush() # flush to get comment.id
    
    # Notify Post Owner (if not self)
    if current_user.id != item.user_id:
        # Avoid duplicate duplicate comment notification if they also tagged the owner
        mentioned_usernames_check = set(re.findall(r'@(\w+)', content))
        if item.user.username not in mentioned_usernames_check:
            notif = Notification(
                recipient_id=item.user_id,
                actor_id=current_user.id,
                item_id=item_id,
                comment_id=comment.id,
                action_type='comment',
                content=f'{current_user.username} đã bình luận: "{content[:60]}...' if len(content)>60 else f'{current_user.username} đã bình luận: "{content}"'
            )
            db.session.add(notif)
            from app.extensions import socketio
            socketio.emit('notification', {
                'message': notif.content,
                'sender_name': 'Bình luận mới',
                'type': 'new_notification'
            }, room=f'user_{item.user_id}')

    # Parse @mentions and create notifications
    for uname in mentioned_usernames:
        tagged_user = User.query.filter_by(username=uname).first()
        if not tagged_user or tagged_user.id == current_user.id:
            continue
        # Regular users cannot tag admins
        if tagged_user.is_admin and not current_user.is_admin:
            continue
        # Check if current_user is blocked by tagged_user
        is_blocked = BlockedUser.query.filter_by(
            user_id=tagged_user.id, blocked_user_id=current_user.id
        ).first()
        if is_blocked:
            continue
            
        # Check if current_user is muted by tagged_user
        is_muted = MutedUser.query.filter_by(
            user_id=tagged_user.id, muted_user_id=current_user.id
        ).first()
        
        if not is_muted:
            notif = Notification(
                recipient_id=tagged_user.id,
                actor_id=current_user.id,
                item_id=item_id,
                comment_id=comment.id,
                action_type='tag',
                content=f'{current_user.username} đã tag bạn trong bài viết "{item.title[:20]}..."'
            )
            db.session.add(notif)
    
            # Real-time SocketIO notification
            try:
                from app.extensions import socketio
                socketio.emit('tag_notification', {
                    'actor_name': current_user.username,
                    'actor_avatar': current_user.avatar,
                    'item_id': item_id,
                    'item_title': item.title,
                    'comment_id': comment.id,
                    'comment_snippet': content[:80]
                }, room=f'user_{tagged_user.id}')
            except Exception:
                pass

    db.session.commit()

    return jsonify({
        'success': True,
        'comment': comment.to_dict(),
        'comment_count': Comment.query.filter_by(item_id=item_id).count()
    })


@bp.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """Delete a comment (only the comment owner can delete)"""
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Bạn không có quyền xóa bình luận này'}), 403

    item_id = comment.item_id
    db.session.delete(comment)
    db.session.commit()

    return jsonify({
        'success': True,
        'comment_count': Comment.query.filter_by(item_id=item_id).count()
    })


# ─── USER SEARCH (for @tagging) ─────────────────────────

@bp.route('/api/users/search')
@login_required
def search_users():
    """Search users for @mention autocomplete"""
    q = request.args.get('q', '').strip()

    # Get IDs of users who blocked current_user
    blocked_by_ids = [b.user_id for b in BlockedUser.query.filter_by(blocked_user_id=current_user.id).all()]

    query = User.query.filter(User.id != current_user.id)
    # Regular users cannot tag admins
    if not current_user.is_admin:
        query = query.filter(User.is_admin != True)
    if blocked_by_ids:
        query = query.filter(~User.id.in_(blocked_by_ids))
    if q:
        query = query.filter(User.username.ilike(f'%{q}%'))
    users = query.order_by(User.username).limit(10).all()

    return jsonify({
        'success': True,
        'users': [{
            'id': u.id,
            'username': u.username,
            'avatar': u.avatar
        } for u in users]
    })


# ─── ITEM RENEWAL (Auto-Expiry specific) ─────────────

from datetime import datetime, timedelta

@bp.route('/api/posts/<int:item_id>/renew', methods=['POST'])
@login_required
def renew_item(item_id):
    """Renew an expiring post for 10 more days (max 3 times)"""
    item = Item.query.get_or_404(item_id)
    
    if item.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Bạn không có quyền gia hạn tin này'}), 403
        
    if item.status != 'Open':
        return jsonify({'success': False, 'message': 'Chỉ có thể gia hạn tin chưa đóng'}), 400
        
    if item.renewal_count >= 3:
        return jsonify({'success': False, 'message': 'Đã hết số lần gia hạn (tối đa 3 lần)'}), 400
        
    item.renewal_count += 1
    item.warning_sent = False
    
    now = datetime.utcnow()
    item.expires_at = now + timedelta(days=10)
    
    # Xóa thông báo cảnh báo cũ nếu có
    Notification.query.filter_by(
        recipient_id=current_user.id,
        item_id=item_id,
        action_type='expiry_warning'
    ).delete()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Gia hạn thành công thêm 10 ngày (còn {3 - item.renewal_count} lần)',
        'renewals_left': 3 - item.renewal_count
    })
