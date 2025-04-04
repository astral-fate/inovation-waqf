from app import db
from datetime import datetime, timezone

class ProjectUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    update_type = db.Column(db.String(50))  # milestone, progress, financial, etc.
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
