# coding: utf-8
from apps.extensions import db
from datetime import datetime

class SyncLog(db.Model):
    __tablename__ = 'sync_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False) # e.g., 'success' or 'failed'
    error_message = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SyncLog {self.status} at {self.timestamp}>'
