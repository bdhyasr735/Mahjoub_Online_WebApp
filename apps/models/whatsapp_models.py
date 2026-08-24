# -*- coding: utf-8 -*-
# 📂 apps/models/whatsapp_models.py

try:
    from apps.extensions import db
except ImportError:
    from app import db

from datetime import datetime

class WhatsAppWebhookEvent(db.Model):
    __tablename__ = 'whatsapp_webhook_events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WhatsAppMessageLog(db.Model):
    __tablename__ = 'whatsapp_message_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    wamid = db.Column(db.String(100), unique=True, nullable=True) # معرف الرسالة لدى ميتا
    direction = db.Column(db.String(20), nullable=False)          # inbound / outbound
    sender_number = db.Column(db.String(30), nullable=False)
    recipient_number = db.Column(db.String(30), nullable=False)
    
    # تفاصيل الرسالة والوسائط (صور وفيديوهات)
    message_type = db.Column(db.String(30), default='text')        # text, image, video, document, audio
    content = db.Column(db.Text, nullable=True)                    # نص الرسالة أو وصف الوسائط
    media_url = db.Column(db.String(500), nullable=True)           # رابط أو مسار الملف (صورة/فيديو)
    media_id = db.Column(db.String(100), nullable=True)            # معرف الميديا في سيرفرات ميتا
    
    status = db.Column(db.String(30), default='received')          # received, sent, delivered, read
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class WhatsAppCustomerContact(db.Model):
    __tablename__ = 'whatsapp_customer_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(30), unique=True, nullable=False)
    
    # الأسماء (القابلة للتعديل يدوياً والحفظ في قاعدة البيانات)
    name = db.Column(db.String(100), nullable=True)                
    whatsapp_profile_name = db.Column(db.String(100), nullable=True) 
    
    # تفاصيل البطاقة الحقيقية (صورة، حالة، وآخر ظهور)
    avatar_url = db.Column(db.String(500), nullable=True)          # رابط صورة العميل
    is_online = db.Column(db.Boolean, default=False)               # حالة الاتصال
    last_seen = db.Column(db.DateTime, nullable=True)              # وقت آخر ظهور
    
    last_message = db.Column(db.Text, nullable=True)
    last_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    unread_count = db.Column(db.Integer, default=0)
    
    # حالة التواصل
    is_blocked = db.Column(db.Boolean, default=False)

    # -------------------------------------------------------------
    # خصائص مساعدة (Properties) متوافقة مع قوالب العرض (chat_view.html)
    # -------------------------------------------------------------
    @property
    def phone_number(self):
        """توافقاً مع القالب الذي يستدعي client.phone_number"""
        return self.phone

    @property
    def total_messages_count(self):
        """حساب إجمالي الرسائل المتبادلة مع هذا الرقم تلقائياً"""
        try:
            return WhatsAppMessageLog.query.filter(
                (WhatsAppMessageLog.sender_number == self.phone) | 
                (WhatsAppMessageLog.recipient_number == self.phone)
            ).count()
        except Exception:
            return 0

    @property
    def orders(self):
        """إرجاع الطلبات المرتبطة بالعميل (يمكن ربطها بجدول الطلبات لديك لاحقاً)"""
        return []

    @property
    def status_label(self):
        return "نشط"
