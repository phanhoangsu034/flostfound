"""
Admin logs routes
"""
from flask import Blueprint, render_template, request
from flask_login import login_required
from app.core.decorators import admin_required
from app.models.action_log import ActionLog
from app.models.user import User
from datetime import datetime, timedelta

bp = Blueprint('admin_logs', __name__)

@bp.route('/admin/logs')
@login_required
@admin_required
def admin_logs():
    search_query = request.args.get('search', '')
    date_query = request.args.get('date', '')
    
    query = ActionLog.query.join(ActionLog.user)
    
    if search_query:
        query = query.filter(
            (ActionLog.action.ilike(f'%{search_query}%')) | 
            (ActionLog.details.ilike(f'%{search_query}%')) |
            (User.username.ilike(f'%{search_query}%'))
        )
        
    if date_query:
        try:
            # Filter by exactly that day
            dt = datetime.strptime(date_query, '%Y-%m-%d')
            # Assuming DB stores in UTC, but user selects local date. 
            # If user selects "2024-03-25", it means 17:00 UTC (25th) to 17:00 UTC (26th) roughly if we want local day.
            # But let's keep it simple: filter by UTC day for now, or use the local math.
            start_of_day = dt
            end_of_day = dt + timedelta(days=1)
            query = query.filter(ActionLog.timestamp >= start_of_day, ActionLog.timestamp < end_of_day)
        except ValueError:
            pass

    logs = query.order_by(ActionLog.timestamp.desc()).all()
    
    # Add local timestamp for display (+7)
    for log in logs:
        log.local_timestamp = log.timestamp + timedelta(hours=7)
        
    return render_template('admin/logs.html', 
                          logs=logs, 
                          search_query=search_query, 
                          date_query=date_query)
