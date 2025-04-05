from models import db
import uuid
from datetime import datetime

class Outreach(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    provider_id = db.Column(db.String, db.ForeignKey('provider.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # email, call, etc.
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime) 