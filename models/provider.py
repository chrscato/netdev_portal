from models import db
import uuid
from datetime import datetime

class Provider(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(128), nullable=False)
    dba_name = db.Column(db.String(128))
    address = db.Column(db.String(256))
    provider_type = db.Column(db.String(50))  # imaging, EMG, etc.
    states_in_contract = db.Column(db.String(256))  # comma-separated
    rate_type = db.Column(db.String(50))  # 'standard' or 'wcfs'
    wcfs_percentage = db.Column(db.Float, nullable=True)
    npi = db.Column(db.String(20))
    specialty = db.Column(db.String(128))
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contacts = db.relationship('Contact', backref='provider', lazy=True)
    outreach = db.relationship('Outreach', backref='provider', lazy=True) 