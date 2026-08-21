# coding: utf-8
# 📂 apps/models/whatsapp_models.py

from app import db
from datetime import datetime

class WhatsAppMessageLog(db.Model):
    __tablename__ = 'whatsapp_message_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    wamid = db.Column(db.String(100), unique=True, nullable=True) # ID الخاص برسالة ميتا
    direction = db.Column(db.String(20), nullable=False) # 'inbound' أو 'outbound'
    sender_number = db.Column(db.String(30), nullable=False, index=True) # فهرس للبحث السريع
    recipient_number = db.Column(db.String(30), nullable=False, index=True)
    order_id = db.Column(db.String(50), nullable=True, index=True)
    message_type = db.Column(db.String(30), default='text')
    content = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='received')
    error_message = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class WhatsAppWebhookEvent(db.Model):
    __tablename__ = 'whatsapp_webhook_events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), default='incoming_payload')
    payload = db.Column(db.JSON, nullable=True) # لتخزين بيانات ميتا الخام
    processed = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class WhatsAppCustomerContact(db.Model):
    __tablename__ = 'whatsapp_customer_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=True)
    last_message = db.Column(db.Text, nullable=True)
    last_timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    unread_count = db.Column(db.Integer, default=0)

# 🔗 نصيحة للمحترفين:
# بعد حفظ هذا الملف، قم باستيراده مرة واحدة في ملف `__init__.py` الخاص بـ `apps/models/` 
# أو في ملف التشغيل الرئيسي لضمان اكتشافه عند تنفيذ `db.create_all()`.