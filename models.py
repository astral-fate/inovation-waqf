from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# User roles
ROLES = {
    'ADMIN': 'admin',
    'PROJECT_OWNER': 'project_owner',
    'FUNDER': 'funder'
}

# Project status types
PROJECT_STATUS = {
    'DRAFT': 'draft',
    'PENDING': 'pending_review',
    'APPROVED': 'approved',
    'FUNDING': 'funding',
    'FUNDED': 'funded',
    'COMPLETED': 'completed',
    'REJECTED': 'rejected'
}

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    profile_image = db.Column(db.String(255), default='default_profile.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    projects = db.relationship('Project', backref='owner', lazy=True, foreign_keys='Project.owner_id')
    funds = db.relationship('Funding', backref='funder', lazy=True)
    watchlist = db.relationship('Watchlist', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == ROLES['ADMIN']
    
    def is_project_owner(self):
        return self.role == ROLES['PROJECT_OWNER']
    
    def is_funder(self):
        return self.role == ROLES['FUNDER']

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    funding_goal = db.Column(db.Float, nullable=False)
    current_funding = db.Column(db.Float, default=0.0)
    funding_progress = db.Column(db.Float, default=0.0)  # Percentage
    expected_return = db.Column(db.String(50))  # e.g. "15-20%"
    image = db.Column(db.String(255), default='default_project.jpg')
    status = db.Column(db.String(20), default=PROJECT_STATUS['DRAFT'])
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    admin_notes = db.Column(db.Text)  # For admin feedback
    
    # Date fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    reviewed_at = db.Column(db.DateTime)
    funding_start_date = db.Column(db.DateTime)
    funding_end_date = db.Column(db.DateTime)
    completion_date = db.Column(db.DateTime)
    
    # Relationships
    funds = db.relationship('Funding', backref='project', lazy=True)
    updates = db.relationship('ProjectUpdate', backref='project', lazy=True)
    watchlist_entries = db.relationship('Watchlist', backref='project', lazy=True)
    
    def calculate_progress(self):
        if self.funding_goal > 0:
            self.funding_progress = (self.current_funding / self.funding_goal) * 100
        return self.funding_progress
    
    def days_remaining(self):
        if self.funding_end_date and self.status == PROJECT_STATUS['FUNDING']:
            delta = self.funding_end_date - datetime.utcnow()
            return max(0, delta.days)
        return 0

class Funding(db.Model):
    __tablename__ = 'fundings'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    funder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Potential returns
    expected_return = db.Column(db.Float)  # Percentage
    actual_return = db.Column(db.Float)    # Actual amount returned
    return_date = db.Column(db.DateTime)

class ProjectUpdate(db.Model):
    __tablename__ = 'project_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    update_type = db.Column(db.String(50))  # e.g. milestone, general, return
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Watchlist(db.Model):
    __tablename__ = 'watchlist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    notification_type = db.Column(db.String(50))  # e.g. project_update, funding, admin_action
    related_id = db.Column(db.Integer)  # ID of related entity (project, funding, etc.)
    date = db.Column(db.DateTime, default=datetime.utcnow)