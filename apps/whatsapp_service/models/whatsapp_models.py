# coding: utf-8
# 📂 apps/models/whatsapp_models.py

"""
SQLAlchemy Database Models for WhatsApp Integration
Moved to global apps/models for automatic discovery by db.create_all()
"""

from datetime import datetime
from app import db 

class WhatsAppMessageLog(db.Model):
    """
    Stores all outbound & inbound messages with delivery receipts and Order links.
    """
    __tablename__ = 'whatsapp_message_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wamid = db.Column(db.String(128), unique=True, index=True, nullable=True)
    direction = db.Column(db.String(16), nullable=False, default='outbound')
    sender_number = db.Column(db.String(32), nullable=False, index=True)
    recipient_number = db.Column(db.String(32), nullable=False, index=True)
    customer_name = db.Column(db.String(128), nullable=True)
    order_id = db.Column(db.String(64), nullable=True, index=True)
    message_type = db.Column(db.String(32), default='text')
    content = db.Column(db.Text, nullable=False)
    template_name = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(32), default='sent', index=True)
    error_message = db.Column(db.Text, nullable=True)
    raw_payload = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        time_val = self.timestamp or self.created_at
        return {
            "id": self.id,
            "wamid": self.wamid,
            "direction": self.direction,
            "sender_number": self.sender_number,
            "recipient_number": self.recipient_number,
            "customer_name": self.customer_name,
            "order_id": self.order_id,
            "message_type": self.message_type,
            "content": self.content,
            "template_name": self.template_name,
            "status": self.status,
            "error_message": self.error_message,
            "timestamp": time_val.isoformat() if time_val else None
        }

class WhatsAppWebhookEvent(db.Model):
    """
    Raw logs of all inbound Webhook payloads.
    """
    __tablename__ = 'whatsapp_webhook_events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_type = db.Column(db.String(64), default='messages')
    payload = db.Column(db.JSON, nullable=False)
    processed = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WhatsAppCustomerContact(db.Model):
    """
    Active customer threads.
    """
    __tablename__ = 'whatsapp_customer_contacts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(32), unique=True, index=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    active_order_id = db.Column(db.String(64), nullable=True)
    unread_count = db.Column(db.Integer, default=0)
    last_message = db.Column(db.Text, nullable=True)
    last_timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)