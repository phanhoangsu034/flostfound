"""
Configuration classes for different environments
"""
import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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
    """Production configuration – requires DATABASE_URL (Postgres on Render)."""
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        if not os.environ.get('SECRET_KEY'):
            raise ValueError("SECRET_KEY environment variable is required in production")
        _db_url = os.environ.get('DATABASE_URL')
        if not _db_url:
            raise ValueError("DATABASE_URL environment variable is required in production")
        if _db_url.startswith("postgres://"):
            _db_url = _db_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif _db_url.startswith("postgresql://"):
            _db_url = _db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        cls.SQLALCHEMY_DATABASE_URI = _db_url
        cls.SECRET_KEY = os.environ.get('SECRET_KEY')


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
