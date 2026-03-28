from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.extensions import db
from app.models.user import User
from app.models.user_preference import BlockedUser, MutedUser, TagReport

bp = Blueprint('users_reporting', __name__)

@bp.route('/api/users/<int:target_id>/mute', methods=['POST'])
@login_required
def toggle_mute_user(target_id):
    """Toggle mute status for a user (stops tag notifications)"""
    if target_id == current_user.id:
        return jsonify({'success': False, 'message': 'Không thể tự mute bản thân.'}), 400

    target = User.query.get_or_404(target_id)
    
    existing = MutedUser.query.filter_by(user_id=target_id, muted_user_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
        muted = False
        message = f"Đã bỏ theo báo (unmute) {target.username}"
    else:
        # Prevent duplicate
        new_mute = MutedUser(user_id=target_id, muted_user_id=current_user.id)
        db.session.add(new_mute)
        muted = True
        message = f"Đã bỏ qua thông báo từ {target.username}"
        
    db.session.commit()
    return jsonify({'success': True, 'muted': muted, 'message': message})


@bp.route('/api/users/<int:target_id>/report_tag', methods=['POST'])
@login_required
def report_tag(target_id):
    """Report a user for tagging abuse"""
    if target_id == current_user.id:
        return jsonify({'success': False, 'message': 'Không thể tự report bản thân.'}), 400

    target = User.query.get_or_404(target_id)
    data = request.get_json() or {}
    reason = data.get('reason', 'spam')
    comment_id = data.get('comment_id')

    # Ensure user hasn't already reported this target recently (e.g. today)
    now = datetime.utcnow()
    recent_report = TagReport.query.filter_by(
        reporter_id=current_user.id, reported_id=target_id
    ).filter(TagReport.created_at >= now - timedelta(days=1)).first()

    if recent_report:
        return jsonify({'success': False, 'message': 'Bạn đã báo cáo người này trong vòng 24 giờ qua. Cảm ơn phản hồi của bạn.'})

    new_report = TagReport(
        reporter_id=current_user.id,
        reported_id=target_id,
        comment_id=comment_id,
        reason=reason
    )
    db.session.add(new_report)

    # Auto-lock logic: If reported by >= 5 different users in 24 hours
    reports_last_24h = TagReport.query.filter_by(reported_id=target_id).filter(
        TagReport.created_at >= now - timedelta(days=1)
    ).all()
    
    unique_reporters = set(r.reporter_id for r in reports_last_24h)
    
    if len(unique_reporters) >= 5:
        target.tagging_locked_until = now + timedelta(days=1)
        # Add a penalty strike
        target.spam_strikes = (target.spam_strikes or 0) + 1
        
    db.session.commit()
    return jsonify({'success': True, 'message': f"Đã gửi báo cáo vi phạm đối với {target.username}. Hệ thống sẽ ghi nhận và xử lý."})


@bp.route('/api/users/<int:target_id>/block', methods=['POST'])
@login_required
def toggle_block_user(target_id):
    """Toggle block status for a user (prevents tagging)"""
    if target_id == current_user.id:
        return jsonify({'success': False, 'message': 'Không thể tự block bản thân.'}), 400

    target = User.query.get_or_404(target_id)
    
    existing = BlockedUser.query.filter_by(user_id=current_user.id, blocked_user_id=target_id).first()
    if existing:
        db.session.delete(existing)
        blocked = False
        message = f"Đã bỏ chặn {target.username}"
    else:
        new_block = BlockedUser(user_id=current_user.id, blocked_user_id=target_id)
        db.session.add(new_block)
        blocked = True
        message = f"Đã chặn {target.username}. Họ sẽ không thể tag bạn từ giờ."
        
    db.session.commit()
    return jsonify({'success': True, 'blocked': blocked, 'message': message})

