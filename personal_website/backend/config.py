"""
Configuration settings for the personal website.
Defines different configurations for development, testing, and production environments.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration settings."""
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'my-secure-secret-key')
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'my-csrf-secret-key')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB max upload size
    UPLOAD_FOLDER = os.path.join('frontend', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'pdf', 'doc', 'docx'}
    
    # Default pagination settings
    DEFAULT_PAGE_SIZE = 10
    
    # Admin settings
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'my-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'your-password')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'your-email@gmail.com')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def init_app(app):
        """Initialize application with the configuration."""
        # Create upload folder if it doesn't exist
        os.makedirs(os.path.join(app.root_path, Config.UPLOAD_FOLDER), exist_ok=True)
        
        # Configure logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
        handler.setLevel(logging.getLevelName(Config.LOG_LEVEL))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)


class DevelopmentConfig(Config):
    """Development configuration settings."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dev.db')
    
    # Enable debug toolbar in development
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class TestingConfig(Config):
    """Testing configuration settings."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///:memory:'
    
    # Disable CSRF protection in tests
    WTF_CSRF_ENABLED = False
    
    # Disable mail sending in tests
    MAIL_SUPPRESS_SEND = True


class ProductionConfig(Config):
    """Production configuration settings."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Production security settings
    WTF_CSRF_SSL_STRICT = True
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # Server-side session
    SESSION_TYPE = 'redis'
    SESSION_REDIS = os.environ.get('REDIS_URL')
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with production settings."""
        Config.init_app(app)
        
        # Production logging to syslog
        import logging
        from logging.handlers import SysLogHandler
        
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)
        
        # Configure SSL if used
        if os.environ.get('SSL_DISABLE', 'False') == 'False':
            from flask_sslify import SSLify
            SSLify(app)


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}