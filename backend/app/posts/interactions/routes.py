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
from app.models.user_preference import BlockedUser

bp = Blueprint('posts_interactions', __name__)


# ─── LIKE ───────────────────────────────────────────────

@bp.route('/api/posts/<int:item_id>/like', methods=['POST'])
@login_required
def toggle_like(item_id):
    """Toggle like on a post (like ↔ unlike)"""
    item = Item.query.get_or_404(item_id)
    existing = Like.query.filter_by(user_id=current_user.id, item_id=item_id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        liked = False
    else:
        new_like = Like(user_id=current_user.id, item_id=item_id)
        db.session.add(new_like)
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
    """Get all comments for a post"""
    item = Item.query.get_or_404(item_id)
    comments = Comment.query.filter_by(item_id=item_id).order_by(Comment.date_posted.desc()).all()

    return jsonify({
        'success': True,
        'comments': [c.to_dict() for c in comments],
        'comment_count': len(comments)
    })


@bp.route('/api/posts/<int:item_id>/comments', methods=['POST'])
@login_required
def add_comment(item_id):
    """Add a new comment to a post"""
    item = Item.query.get_or_404(item_id)
    data = request.get_json()

    content = data.get('content', '').strip() if data else ''
    if not content:
        return jsonify({'success': False, 'message': 'Nội dung bình luận không được để trống'}), 400

    if len(content) > 500:
        return jsonify({'success': False, 'message': 'Bình luận tối đa 500 ký tự'}), 400

    comment = Comment(
        content=content,
        user_id=current_user.id,
        item_id=item_id
    )
    db.session.add(comment)
    db.session.commit()

    # Parse @mentions and create notifications
    mentioned_usernames = set(re.findall(r'@(\w+)', content))
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
        notif = Notification(
            recipient_id=tagged_user.id,
            actor_id=current_user.id,
            item_id=item_id,
            comment_id=comment.id,
            action_type='tag',
            content=f'{current_user.username} đã nhắc đến bạn trong một bình luận'
        )
        db.session.add(notif)

        # Real-time SocketIO notification
        from app.extensions import socketio
        socketio.emit('tag_notification', {
            'actor_name': current_user.username,
            'actor_avatar': current_user.avatar,
            'item_id': item_id,
            'item_title': item.title,
            'comment_snippet': content[:80]
        }, room=f'user_{tagged_user.id}')

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
