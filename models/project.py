from app import db
from datetime import datetime, timedelta, timezone

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # tech, medical, industrial, etc.
    funding_goal = db.Column(db.Integer, nullable=False)
    current_funding = db.Column(db.Integer, default=0)
    funding_progress = db.Column(db.Float, default=0)
    expected_return = db.Column(db.String(50))
    image = db.Column(db.String(200))
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    submitted_at = db.Column(db.DateTime, nullable=True)  # Field needed for ordering
    reviewed_at = db.Column(db.DateTime, nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    funding_start_date = db.Column(db.DateTime)
    funding_end_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    fundings = db.relationship('Funding', backref='project', lazy=True)
    
    def calculate_progress(self):
        if self.funding_goal > 0:
            self.funding_progress = min(100, (self.current_funding / self.funding_goal) * 100)
        return self.funding_progress
    
    def days_remaining(self):
        if not self.funding_end_date:
            return 0
        
        # Make funding_end_date timezone-aware if it's not already
        if self.funding_end_date.tzinfo is None:
            # Convert naive datetime to aware datetime using UTC
            aware_end_date = self.funding_end_date.replace(tzinfo=timezone.utc)
        else:
            aware_end_date = self.funding_end_date
            
        delta = aware_end_date - datetime.now(timezone.utc)
        return max(0, delta.days)
