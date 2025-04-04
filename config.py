import os
from datetime import timedelta

class Config:
    # Basic config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///waqf_innovation.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload config
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Flask-Login config
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # Application specific config
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@waqf-innovation.sa')
    PROJECT_APPROVAL_THRESHOLD = 3  # Number of admin approvals needed (for future use)
    DEFAULT_FUNDING_DURATION = 60  # Default funding period in days
    PLATFORM_FEE_PERCENTAGE = 5  # Platform fee on successful funding

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    # In production, set a strong secret key
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Use PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

# Select configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Return the appropriate configuration object based on the environment."""
    config_name = os.environ.get('FLASK_ENV', 'default')
    return config.get(config_name, config['default'])