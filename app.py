import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, generate_csrf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_for_testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///waqf.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    
    # Initialize extensions with app
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
    os.makedirs(os.path.join(app.root_path, 'static', 'uploads', 'projects'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'static', 'uploads', 'profiles'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'static', 'images'), exist_ok=True)
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Import blueprints - moved inside to avoid circular imports
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
    
    # User loader for Flask-Login
    from models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
    
    # Make constants available to templates
    @app.context_processor
    def inject_constants():
        from models import ROLES, PROJECT_STATUS
        return {
            'ROLES': ROLES,
            'PROJECT_STATUS': PROJECT_STATUS
        }
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)