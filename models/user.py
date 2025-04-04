from flask_login import UserMixin
from app import db
from models.constants import ROLES
from werkzeug.security import generate_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'admin', 'funder', or 'project_owner'
    profile_image = db.Column(db.String(200), default='images/default_profile.jpg')
    created_at = db.Column(db.DateTime, nullable=False)
    
    # Relationships
    projects = db.relationship('Project', backref='owner', lazy=True)
    fundings = db.relationship('Funding', backref='funder', lazy=True)
    watchlist = db.relationship('WatchlistItem', backref='user', lazy=True)
    
    # Helper methods to check user roles
    def is_admin(self):
        return self.user_type == ROLES['ADMIN']
    
    def is_funder(self):
        return self.user_type == ROLES['FUNDER']
    
    def is_project_owner(self):
        return self.user_type == ROLES['PROJECT_OWNER']
        
    def set_password(self, password):
        self.password = generate_password_hash(password)
