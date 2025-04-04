from app import db
from datetime import datetime, timezone

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # funding, project_update, etc.
    related_id = db.Column(db.Integer)  # ID of related object (project, etc.)
    is_read = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
