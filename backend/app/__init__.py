"""
Flask application factory
"""
import os
from flask import Flask

def create_app(config_name=None):
    """Create and configure the Flask application"""
    app = Flask(__name__, 
                template_folder='../../frontend/templates',
                static_folder='../../frontend/static')
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Ensure instance folder exists
    os.makedirs(app.config['INSTANCE_DIR'], exist_ok=True)

    # Initialize Cloudinary from CLOUDINARY_URL environment variable
    cloudinary_url = os.environ.get('CLOUDINARY_URL')
    if cloudinary_url:
        import cloudinary
        cloudinary.config(cloudinary_url=cloudinary_url)
    
    # Initialize extensions
    from app.extensions import db, login_manager, socketio
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_login.login'
    socketio.init_app(app)

    # Register core hooks
    from app.core.hooks import register_hooks
    register_hooks(app)
    
    # Register blueprints (this imports all model classes)
    register_blueprints(app)

    # Create DB tables AFTER blueprints are registered
    # so all models (User, Item, etc.) are already imported
    with app.app_context():
        db.create_all()
    
    return app

def register_blueprints(app):
    """Register all application blueprints"""
    # Auth blueprints
    from app.auth.login.routes import bp as auth_login_bp
    from app.auth.register.routes import bp as auth_register_bp
    from app.auth.logout.routes import bp as auth_logout_bp
    from app.auth.password_reset.routes import bp as auth_password_reset_bp
    
    # Posts blueprints
    from app.posts.view.routes import bp as posts_view_bp
    from app.posts.create.routes import bp as posts_create_bp
    from app.posts.delete.routes import bp as posts_delete_bp
    from app.posts.update.routes import bp as posts_update_bp
    
    # Messages blueprints
    from app.messages.chat.routes import bp as messages_chat_bp
    from app.messages.inbox.routes import bp as messages_inbox_bp
    
    # Admin blueprints
    from app.admin.dashboard.routes import bp as admin_dashboard_bp
    from app.admin.posts.routes import bp as admin_posts_bp
    from app.admin.logs.routes import bp as admin_logs_bp
    
    # Profile blueprint
    from app.profile.routes import bp as profile_bp
    
    # Search & Filter blueprint
    from app.search.routes import bp as search_bp
    
    # Register all blueprints
    app.register_blueprint(auth_login_bp)
    app.register_blueprint(auth_register_bp)
    app.register_blueprint(auth_logout_bp)
    app.register_blueprint(auth_password_reset_bp)
    app.register_blueprint(posts_view_bp)
    app.register_blueprint(posts_create_bp)
    app.register_blueprint(posts_delete_bp)
    app.register_blueprint(posts_update_bp)
    app.register_blueprint(messages_chat_bp)
    app.register_blueprint(messages_inbox_bp)
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(admin_posts_bp)
    app.register_blueprint(admin_logs_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(search_bp)
    
    # Register SocketIO events
    from app.messages.socketio import events

# Import socketio to make it accessible from app module
from app.extensions import socketio
