"""
Delete post routes
"""
from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.item import Item
from app.models.action_log import ActionLog

bp = Blueprint('posts_delete', __name__)

@bp.route('/post/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_post(item_id):
    item = Item.query.get_or_404(item_id)
    
    # Check permission: Admin or Owner
    if not current_user.is_admin and current_user.id != item.user_id:
        flash('Bạn không có quyền xóa bài này.', 'danger')
        return redirect(url_for('posts_view.index'))
        
    # Log the deletion
    action_type = "Admin Xóa bài" if current_user.is_admin and current_user.id != item.user_id else "Người dùng xóa bài"
    log = ActionLog(user_id=current_user.id, action=action_type, details=f"Đã xóa bài: {item.title}")
    db.session.add(log)
    
    db.session.delete(item)
    db.session.commit()
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return {'success': True, 'message': 'Đã xóa bài đăng!'}

    flash('Đã xóa bài đăng.', 'success')
    
    # Redirect back to where they came from if possible, or default
    if request.referrer and 'admin' in request.referrer:
        return redirect(url_for('admin_posts.admin_posts'))
    elif request.referrer and 'profile' in request.referrer:
        return redirect(url_for('profile.profile'))
    else:
        return redirect(url_for('posts_view.index'))
