# coding: utf-8
# 📂 apps/whatsapp_service/models/whatsapp_models.py

"""
SQLAlchemy Database Models for WhatsApp Integration
===================================================
Linked with Mahgoob Online Core Database Models (Order, User)
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

# Import db base from core app or define standalone
try:
    from app import db
    BaseModel = db.Model
except Exception:
    from sqlalchemy.ext.declarative import declarative_base
    BaseModel = declarative_base()

class WhatsAppMessageLog(BaseModel):
    """
    Stores all outbound & inbound messages with delivery receipts and Order links.
    """
    __tablename__ = 'whatsapp_message_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    wamid = Column(String(128), unique=True, index=True, nullable=True, comment="Meta Message ID")
    direction = Column(String(16), nullable=False, default='outbound', comment="inbound or outbound")
    sender_number = Column(String(32), nullable=False, index=True)
    recipient_number = Column(String(32), nullable=False, index=True)
    customer_name = Column(String(128), nullable=True)
    
    # ForeignKey relation to core Order table
    order_id = Column(String(64), nullable=True, index=True, comment="e.g. ORD-2409")
    
    message_type = Column(String(32), default='text', comment="text, template, image, document")
    content = Column(Text, nullable=False)
    template_name = Column(String(64), nullable=True)
    
    # Status: sent, delivered, read, received, failed
    status = Column(String(32), default='sent', index=True)
    error_message = Column(Text, nullable=True)
    
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)  # حقل مضاف للتوافق التام مع الكنترولر
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

class WhatsAppWebhookEvent(BaseModel):
    """
    Raw logs of all inbound Webhook payloads from Meta for audit and debugging.
    """
    __tablename__ = 'whatsapp_webhook_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(64), default='messages', comment="messages, statuses, error")
    payload = Column(JSON, nullable=False)
    processed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class WhatsAppCustomerContact(BaseModel):
    """
    Active customer threads with last message snippet and unread badges.
    """
    __tablename__ = 'whatsapp_customer_contacts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(32), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    active_order_id = Column(String(64), nullable=True)
    unread_count = Column(Integer, default=0)
    last_message = Column(Text, nullable=True)
    last_timestamp = Column(DateTime, default=datetime.utcnow)
