from models import db
import uuid
from datetime import datetime

class Contact(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    provider_id = db.Column(db.String, db.ForeignKey('provider.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    title = db.Column(db.String(128))
    email = db.Column(db.String(128))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    preferred_contact_method = db.Column(db.String(20)) 