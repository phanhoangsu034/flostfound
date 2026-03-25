"""
Configuration classes for different environments
"""
import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 600 # 10 minutes session
    SESSION_REFRESH_EACH_REQUEST = True
    REMEMBER_COOKIE_DURATION = 600 # 10 minutes remember-me cookie

    # Instance directory for uploaded files, AI models, etc.
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(os.path.dirname(BASE_DIR), 'instance')


class DevelopmentConfig(Config):
    """Development configuration – uses SQLite so no Postgres needed locally."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or 'sqlite:///' + os.path.join(Config.INSTANCE_DIR, 'flostfound.db')
    )


class ProductionConfig(Config):
    """Production configuration – Railway / Render.
    Falls back to SQLite if DATABASE_URL is not yet configured.
    """
    DEBUG = False

    # Convert DATABASE_URL at class load time (Railway provides postgres:// scheme)
    _db_url = os.environ.get('DATABASE_URL', '')
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif _db_url.startswith("postgresql://"):
        _db_url = _db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    # Fallback to SQLite so the app can start even without Postgres
    SQLALCHEMY_DATABASE_URI = (
        _db_url
        or 'sqlite:///' + os.path.join(Config.INSTANCE_DIR, 'flostfound.db')
    )
    SECRET_KEY = os.environ.get('SECRET_KEY') or Config.SECRET_KEY

    @classmethod
    def init_app(cls, app):
        pass  # All setup is done at class level


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('TEST_DATABASE_URL')
        or os.environ.get('DATABASE_URL')
        or 'sqlite:///test.db'
    )


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
