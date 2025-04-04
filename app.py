import os
import sys
import logging
from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, generate_csrf
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    logger.info("Starting Flask application creation")
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_for_testing')
    
    # Database configuration - simplified for Railway
    db_path = os.path.join(os.getcwd(), 'waqf.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    logger.info(f"Using database at: {db_path}")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    logger.info(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # File storage configuration
    app.config['USE_S3'] = os.getenv('USE_S3', 'False').lower() == 'true'
    app.config['S3_BUCKET_NAME'] = os.getenv('S3_BUCKET_NAME', '')
    app.config['AWS_REGION'] = os.getenv('AWS_REGION', 'us-east-1')
    
    # Local file storage (used when S3 is not configured)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    
    # Initialize extensions with app
    logger.info("Initializing Flask extensions")
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
    login_manager.login_message_category = 'info'
    migrate.init_app(app, db)
    
    # Make CSRF token available in all templates
    app.jinja_env.globals['csrf_token'] = generate_csrf
    
    # Create required directories for file uploads
    try:
        logger.info("Creating required directories")
        os.makedirs(os.path.join(app.root_path, 'static', 'uploads', 'projects'), exist_ok=True)
        os.makedirs(os.path.join(app.root_path, 'static', 'uploads', 'profiles'), exist_ok=True)
        os.makedirs(os.path.join(app.root_path, 'static', 'images'), exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        logger.info("Directories created successfully")
    except Exception as e:
        logger.error(f"Error creating directories: {str(e)}")
    
    # Import blueprints - moved inside to avoid circular imports
    try:
        logger.info("Registering blueprints")
        with app.app_context():
            from routes.auth import auth_bp
            from routes.main import main_bp
            from routes.funder import funder_bp
            from routes.project_owner import project_owner_bp
            from routes.admin import admin_bp
            
            # Register blueprints
            app.register_blueprint(auth_bp)
            app.register_blueprint(main_bp)
            app.register_blueprint(funder_bp, url_prefix='/funder')
            app.register_blueprint(project_owner_bp, url_prefix='/project-owner')
            app.register_blueprint(admin_bp, url_prefix='/admin')
        logger.info("Blueprints registered successfully")
    except Exception as e:
        logger.error(f"Error registering blueprints: {str(e)}", exc_info=True)
        raise
    
    # User loader for Flask-Login
    from models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            logger.error(f"Error loading user {user_id}: {str(e)}")
            return None
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        logger.warning(f"404 error: {request.path}")
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"500 error: {str(e)}")
        return render_template('500.html'), 500
    
    # Make constants available to templates
    @app.context_processor
    def inject_constants():
        try:
            from models import ROLES, PROJECT_STATUS
            return {
                'ROLES': ROLES,
                'PROJECT_STATUS': PROJECT_STATUS
            }
        except Exception as e:
            logger.error(f"Error injecting constants: {str(e)}")
            return {}
    
    # Create database tables
    try:
        logger.info("Creating database tables")
        with app.app_context():
            db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}", exc_info=True)
    
    # Add Jinja template function to get file URLs
    @app.template_filter('file_url')
    def file_url_filter(file_path):
        """Get the appropriate URL for a file based on storage configuration"""
        try:
            if not file_path:
                return url_for('static', filename='images/default.jpg')
                
            if app.config['USE_S3']:
                # Use the S3 URL
                try:
                    from utils.s3_storage import get_file_url
                    return get_file_url(file_path)
                except Exception as e:
                    logger.error(f"Error getting S3 URL for {file_path}: {str(e)}")
                    return url_for('static', filename='images/default.jpg')
            else:
                # For local storage, just return the static URL
                return url_for('static', filename=file_path)
        except Exception as e:
            logger.error(f"Error in file_url_filter: {str(e)}")
            return url_for('static', filename='images/default.jpg')
    
    # Add a route to test the application
    @app.route('/healthcheck')
    def healthcheck():
        return 'OK', 200
    
    logger.info("Application creation completed successfully")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
