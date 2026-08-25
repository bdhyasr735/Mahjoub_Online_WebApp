# -*- coding: utf-8 -*-
# 📂 apps/models/whatsapp_models.py

try:
    from apps.extensions import db
except ImportError:
    from app import db

from datetime import datetime
import os
import json


class WhatsAppWebhookEvent(db.Model):
    """تخزين أحداث Webhook الخام للتصحيح والتتبع"""
    __tablename__ = 'whatsapp_webhook_events'
    
    __table_args__ = (
        db.Index('idx_webhook_created', 'created_at'),
        db.Index('idx_webhook_processed', 'processed'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WhatsAppMessageLog(db.Model):
    """سجل شامل للرسائل الصادرة والواردة"""
    __tablename__ = 'whatsapp_message_logs'
    
    __table_args__ = (
        db.Index('idx_msg_sender', 'sender_number'),
        db.Index('idx_msg_recipient', 'recipient_number'),
        db.Index('idx_msg_wamid', 'wamid'),
        db.Index('idx_msg_timestamp', 'timestamp'),
        db.Index('idx_msg_status', 'status'),
        db.Index('idx_msg_direction', 'direction'),
        db.Index('idx_msg_customer', 'customer_id'),
        db.Index('idx_msg_conversation', 'conversation_id'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    wamid = db.Column(db.String(100), unique=True, nullable=True)
    message_id = db.Column(db.String(100), unique=True, nullable=True)
    direction = db.Column(db.String(20), nullable=False)          # inbound / outbound
    sender_number = db.Column(db.String(30), nullable=False)
    recipient_number = db.Column(db.String(30), nullable=False)
    conversation_id = db.Column(db.String(100), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('whatsapp_customer_contacts.id'), nullable=True)
    user_id = db.Column(db.Integer, nullable=True)               # معرف المسؤول/الوكيل
    message_type = db.Column(db.String(30), default='text')
    content = db.Column(db.Text, nullable=True)
    # وسائط
    media_url = db.Column(db.String(500), nullable=True)
    media_id = db.Column(db.String(100), nullable=True)
    media_filename = db.Column(db.String(200), nullable=True)
    media_filesize = db.Column(db.Integer, nullable=True)
    media_mime_type = db.Column(db.String(100), nullable=True)
    media_caption = db.Column(db.Text, nullable=True)
    # موقع
    location_latitude = db.Column(db.Float, nullable=True)
    location_longitude = db.Column(db.Float, nullable=True)
    location_name = db.Column(db.String(200), nullable=True)
    location_address = db.Column(db.String(200), nullable=True)
    # جهة اتصال
    contact_name = db.Column(db.String(200), nullable=True)
    contact_phone = db.Column(db.String(30), nullable=True)
    contact_email = db.Column(db.String(100), nullable=True)
    contact_organization = db.Column(db.String(100), nullable=True)
    # ملصق
    sticker_package_id = db.Column(db.String(50), nullable=True)
    sticker_id = db.Column(db.String(50), nullable=True)
    # تفاعلي
    interactive_type = db.Column(db.String(30), nullable=True)
    interactive_payload = db.Column(db.JSON, nullable=True)
    # قالب
    template_name = db.Column(db.String(100), nullable=True)
    template_language = db.Column(db.String(10), nullable=True)
    template_components = db.Column(db.JSON, nullable=True)
    # رد
    reply_to_message_id = db.Column(db.String(100), nullable=True)
    reply_to_content = db.Column(db.Text, nullable=True)
    # حالة
    status = db.Column(db.String(30), default='received')
    is_forwarded = db.Column(db.Boolean, default=False)
    forwarded_from = db.Column(db.String(30), nullable=True)
    mentioned_ids = db.Column(db.JSON, nullable=True)
    reactions = db.Column(db.JSON, nullable=True)
    # توقيت
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_outbound(self):
        return self.direction == 'outbound'
    
    @property
    def is_inbound(self):
        return self.direction == 'inbound'
    
    @property
    def is_successful(self):
        return self.status in ('sent', 'delivered', 'read')
    
    @property
    def is_failed(self):
        return self.status == 'failed'
    
    def to_dict(self):
        return {
            'id': self.id,
            'wamid': self.wamid,
            'direction': self.direction,
            'sender': self.sender_number,
            'recipient': self.recipient_number,
            'content': self.content,
            'message_type': self.message_type,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


class WhatsAppCustomerContact(db.Model):
    """جهات اتصال العملاء مع معلومات الحالة وآخر رسالة"""
    __tablename__ = 'whatsapp_customer_contacts'
    
    __table_args__ = (
        db.Index('idx_contact_phone', 'phone'),
        db.Index('idx_contact_last_timestamp', 'last_timestamp'),
        db.Index('idx_contact_unread', 'unread_count'),
        db.Index('idx_contact_customer', 'customer_id'),
        db.Index('idx_contact_supplier', 'supplier_id'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    whatsapp_profile_name = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, nullable=True)
    last_message = db.Column(db.Text, nullable=True)
    # last_message_id محذوف (غير موجود في قاعدة البيانات)
    last_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    unread_count = db.Column(db.Integer, default=0)
    is_blocked = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    tags = db.Column(db.JSON, nullable=True)
    extra_data = db.Column(db.JSON, nullable=True)
    customer_id = db.Column(db.Integer, nullable=True)
    supplier_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def phone_number(self):
        return self.phone
    
    @property
    def total_messages_count(self):
        try:
            return WhatsAppMessageLog.query.filter(
                (WhatsAppMessageLog.sender_number == self.phone) |
                (WhatsAppMessageLog.recipient_number == self.phone)
            ).count()
        except Exception:
            return 0
    
    @property
    def orders(self):
        """يمكن ربط الطلبات هنا مستقبلاً"""
        return []
    
    @property
    def status_label(self):
        if self.is_blocked:
            return "محظور"
        return "نشط"
    
    @property
    def display_name(self):
        return self.name or self.whatsapp_profile_name or f"عميل ({self.phone})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'name': self.display_name,
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'last_message': self.last_message,
            'last_timestamp': self.last_timestamp.isoformat() if self.last_timestamp else None,
            'unread_count': self.unread_count,
        }


class WhatsAppSettings(db.Model):
    """إعدادات خدمة واتساب (مفتاح/قيمة)"""
    __tablename__ = 'whatsapp_settings'
    
    __table_args__ = (
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_setting(cls, key, default=""):
        try:
            setting = cls.query.filter_by(key=key).first()
            if setting and setting.value is not None:
                return setting.value
        except Exception:
            pass
        return os.getenv(key, default)
    
    @classmethod
    def set_setting(cls, key, value):
        try:
            setting = cls.query.filter_by(key=key).first()
            if setting:
                setting.value = value
                setting.updated_at = datetime.utcnow()
            else:
                setting = cls(key=key, value=value)
                db.session.add(setting)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False


class WhatsAppTemplate(db.Model):
    """قوالب واتساب المعتمدة مسبقاً"""
    __tablename__ = 'whatsapp_templates'
    
    __table_args__ = (
        db.Index('idx_template_name_lang', 'name', 'language'),
        db.Index('idx_template_status', 'status'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(30), default='pending')
    components = db.Column(db.JSON, nullable=False)
    namespace = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WhatsAppConversation(db.Model):
    """جلسات المحادثة (لتجميع الرسائل في محادثات متعددة)"""
    __tablename__ = 'whatsapp_conversations'
    
    __table_args__ = (
        db.Index('idx_conv_customer', 'customer_id'),
        db.Index('idx_conv_last_at', 'last_message_at'),
        db.Index('idx_conv_active', 'is_active'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.String(100), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('whatsapp_customer_contacts.id'), nullable=True)
    supplier_id = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_archived = db.Column(db.Boolean, default=False)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_preview = db.Column(db.Text, nullable=True)
    total_messages = db.Column(db.Integer, default=0)
    unread_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WhatsAppMediaCache(db.Model):
    """تخزين مؤقت للوسائط (لتجنب إعادة تحميل الملفات من ميتا)"""
    __tablename__ = 'whatsapp_media_cache'
    
    __table_args__ = (
        db.Index('idx_media_id', 'media_id'),
        db.Index('idx_media_expires', 'expires_at'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.String(100), unique=True, nullable=False)
    url = db.Column(db.String(500), nullable=False)
    mime_type = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    file_name = db.Column(db.String(200), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
