from models import db
import uuid
from datetime import datetime

class Outreach(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    provider_id = db.Column(db.String, db.ForeignKey('provider.id'), nullable=False)
    contact_id = db.Column(db.String, db.ForeignKey('contact.id'), nullable=True)
    method = db.Column(db.String(50))
    notes = db.Column(db.Text)
    status = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) 