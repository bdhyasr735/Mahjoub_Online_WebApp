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
    """تخزين أحداث Webhook الخام من ميتا للتصحيح والتتبع"""
    __tablename__ = 'whatsapp_webhook_events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # فهارس للبحث السريع
    __table_args__ = (
        db.Index('idx_webhook_created', 'created_at'),
        db.Index('idx_webhook_processed', 'processed'),
    )


class WhatsAppMessageLog(db.Model):
    """سجل شامل للرسائل (صادرة وواردة) مع كافة التفاصيل"""
    __tablename__ = 'whatsapp_message_logs'
    
    # المعرف الأساسي
    id = db.Column(db.Integer, primary_key=True)
    
    # معرفات خارجية
    wamid = db.Column(db.String(100), unique=True, nullable=True)  # معرف ميتا
    message_id = db.Column(db.String(100), unique=True, nullable=True)  # معرف داخلي
    
    # اتجاه الرسالة
    direction = db.Column(db.String(20), nullable=False)  # inbound / outbound
    
    # معلومات المرسل والمستلم
    sender_number = db.Column(db.String(30), nullable=False)
    recipient_number = db.Column(db.String(30), nullable=False)
    
    # معرف المحادثة والعميل (للربط)
    conversation_id = db.Column(db.String(100), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('whatsapp_customer_contacts.id'), nullable=True)
    user_id = db.Column(db.Integer, nullable=True)  # معرف المستخدم (الوكيل) الذي أرسل أو استقبل
    
    # تفاصيل الرسالة الأساسية
    message_type = db.Column(db.String(30), default='text')  # text, image, video, document, audio, location, contact, sticker, interactive, template
    
    # المحتوى النصي (لجميع الأنواع، إن وجد)
    content = db.Column(db.Text, nullable=True)
    
    # معلومات الوسائط (للصور والفيديوهات والمستندات والصوت)
    media_url = db.Column(db.String(500), nullable=True)      # رابط الملف (مؤقت)
    media_id = db.Column(db.String(100), nullable=True)       # معرف الميديا في ميتا
    media_filename = db.Column(db.String(200), nullable=True) # اسم الملف الأصلي
    media_filesize = db.Column(db.Integer, nullable=True)     # حجم الملف بالبايت
    media_mime_type = db.Column(db.String(100), nullable=True) # نوع الملف (image/jpeg, etc.)
    media_caption = db.Column(db.Text, nullable=True)         # نص تعليق للصورة/الفيديو/المستند
    
    # معلومات الموقع (للرسائل من نوع location)
    location_latitude = db.Column(db.Float, nullable=True)
    location_longitude = db.Column(db.Float, nullable=True)
    location_name = db.Column(db.String(200), nullable=True)  # اسم المكان
    location_address = db.Column(db.String(200), nullable=True)  # عنوان المكان
    
    # معلومات جهة الاتصال (للرسائل من نوع contact)
    contact_name = db.Column(db.String(200), nullable=True)
    contact_phone = db.Column(db.String(30), nullable=True)
    contact_email = db.Column(db.String(100), nullable=True)
    contact_organization = db.Column(db.String(100), nullable=True)
    
    # معلومات الملصق (sticker)
    sticker_package_id = db.Column(db.String(50), nullable=True)
    sticker_id = db.Column(db.String(50), nullable=True)
    
    # الرسائل التفاعلية (أزرار، قوائم)
    interactive_type = db.Column(db.String(30), nullable=True)  # button, list, reply
    interactive_payload = db.Column(db.JSON, nullable=True)    # بيانات التفاعل (JSON)
    
    # القوالب (templates)
    template_name = db.Column(db.String(100), nullable=True)
    template_language = db.Column(db.String(10), nullable=True)
    template_components = db.Column(db.JSON, nullable=True)    # مكونات القالب (JSON)
    
    # الرد على رسالة معينة
    reply_to_message_id = db.Column(db.String(100), nullable=True)  # wamid للمرسلة الأصلية
    reply_to_content = db.Column(db.Text, nullable=True)            # نص الرسالة الأصلية (للعرض)
    
    # حالة الرسالة
    status = db.Column(db.String(30), default='received')  # received, sent, delivered, read, failed, deleted
    
    # معلومات إضافية
    is_forwarded = db.Column(db.Boolean, default=False)
    forwarded_from = db.Column(db.String(30), nullable=True)  # رقم المرسل الأصلي
    mentioned_ids = db.Column(db.JSON, nullable=True)         # قائمة المعرفات المذكورة
    reactions = db.Column(db.JSON, nullable=True)             # تفاعلات (JSON)
    
    # التوقيت
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # آخر تحديث للحالة
    
    # فهارس للبحث السريع
    __table_args__ = (
        db.Index('idx_msg_sender', 'sender_number'),
        db.Index('idx_msg_recipient', 'recipient_number'),
        db.Index('idx_msg_wamid', 'wamid'),
        db.Index('idx_msg_timestamp', 'timestamp'),
        db.Index('idx_msg_status', 'status'),
        db.Index('idx_msg_direction', 'direction'),
        db.Index('idx_msg_customer', 'customer_id'),
        db.Index('idx_msg_conversation', 'conversation_id'),
    )
    
    # خصائص مساعدة
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


class WhatsAppCustomerContact(db.Model):
    """جهات اتصال العملاء (معلومات كاملة)"""
    __tablename__ = 'whatsapp_customer_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(30), unique=True, nullable=False)
    
    # الأسماء
    name = db.Column(db.String(100), nullable=True)                # الاسم المعروض (قابل للتعديل)
    whatsapp_profile_name = db.Column(db.String(100), nullable=True)  # اسم الملف الشخصي من واتساب
    
    # الصورة والحالة
    avatar_url = db.Column(db.String(500), nullable=True)          # رابط صورة العميل
    is_online = db.Column(db.Boolean, default=False)               # حالة الاتصال (حقيقي)
    last_seen = db.Column(db.DateTime, nullable=True)              # وقت آخر ظهور (من واتساب)
    
    # آخر رسالة وتفاصيل المحادثة
    last_message = db.Column(db.Text, nullable=True)
    last_message_id = db.Column(db.Integer, nullable=True)         # معرف آخر رسالة (ربط)
    last_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    unread_count = db.Column(db.Integer, default=0)
    
    # حالة التواصل
    is_blocked = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)             # أرشيف المحادثة
    
    # معلومات إضافية (قابلة للتوسع)
    notes = db.Column(db.Text, nullable=True)                      # ملاحظات المدير
    tags = db.Column(db.JSON, nullable=True)                       # علامات (tags) لتصنيف العملاء
    metadata = db.Column(db.JSON, nullable=True)                   # بيانات إضافية (مخصصة)
    
    # الربط بنماذج أخرى (مثل العملاء)
    customer_id = db.Column(db.Integer, nullable=True)             # معرف العميل في نظامك الأساسي
    supplier_id = db.Column(db.Integer, nullable=True)             # معرف المورد (إن وجد)
    
    # توقيت الإنشاء والتحديث
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # فهارس
    __table_args__ = (
        db.Index('idx_contact_phone', 'phone'),
        db.Index('idx_contact_last_timestamp', 'last_timestamp'),
        db.Index('idx_contact_unread', 'unread_count'),
        db.Index('idx_contact_customer', 'customer_id'),
        db.Index('idx_contact_supplier', 'supplier_id'),
    )
    
    # خصائص مساعدة
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
        """إرجاع الطلبات المرتبطة (يمكن تخصيصها حسب نظامك)"""
        return []
    
    @property
    def status_label(self):
        if self.is_blocked:
            return "محظور"
        return "نشط"
    
    @property
    def display_name(self):
        return self.name or self.whatsapp_profile_name or f"عميل ({self.phone})"


class WhatsAppSettings(db.Model):
    """إعدادات خدمة واتساب (مفتاح/قيمة)"""
    __tablename__ = 'whatsapp_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_setting(cls, key, default=""):
        """جلب قيمة إعداد معين من قاعدة البيانات أو البيئة"""
        try:
            setting = cls.query.filter_by(key=key).first()
            if setting and setting.value is not None:
                return setting.value
        except Exception:
            pass
        return os.getenv(key, default)
    
    @classmethod
    def set_setting(cls, key, value):
        """حفظ أو تحديث إعداد معين في قاعدة البيانات"""
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
    """قوالب واتساب (للرسائل المعتمدة مسبقاً)"""
    __tablename__ = 'whatsapp_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)          # اسم القالب
    language = db.Column(db.String(10), nullable=False)       # اللغة (ar, en, etc.)
    category = db.Column(db.String(50), nullable=True)        # الفئة (MARKETING, UTILITY, AUTHENTICATION)
    status = db.Column(db.String(30), default='pending')      # pending, approved, rejected, paused
    components = db.Column(db.JSON, nullable=False)           # مكونات القالب (JSON)
    namespace = db.Column(db.String(100), nullable=True)      # Namespace الخاص بالقالب
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_template_name_lang', 'name', 'language'),
        db.Index('idx_template_status', 'status'),
    )


class WhatsAppConversation(db.Model):
    """جلسات المحادثة (لتجميع الرسائل في محادثات متعددة)"""
    __tablename__ = 'whatsapp_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.String(100), unique=True, nullable=False)  # معرف المحادثة من واتساب
    customer_id = db.Column(db.Integer, db.ForeignKey('whatsapp_customer_contacts.id'), nullable=True)
    supplier_id = db.Column(db.Integer, nullable=True)          # معرف المورد (إن وجد)
    
    # معلومات المحادثة
    title = db.Column(db.String(200), nullable=True)            # عنوان المحادثة (اختياري)
    is_active = db.Column(db.Boolean, default=True)
    is_archived = db.Column(db.Boolean, default=False)
    
    # آخر نشاط
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_preview = db.Column(db.Text, nullable=True)
    
    # إحصائيات
    total_messages = db.Column(db.Integer, default=0)
    unread_count = db.Column(db.Integer, default=0)
    
    # توقيت الإنشاء
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # فهارس
    __table_args__ = (
        db.Index('idx_conv_customer', 'customer_id'),
        db.Index('idx_conv_last_at', 'last_message_at'),
        db.Index('idx_conv_active', 'is_active'),
    )


class WhatsAppMediaCache(db.Model):
    """تخزين مؤقت للوسائط (لتجنب إعادة تحميل الملفات من ميتا)"""
    __tablename__ = 'whatsapp_media_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.String(100), unique=True, nullable=False)  # معرف الميديا من ميتا
    url = db.Column(db.String(500), nullable=False)           # رابط الملف المؤقت
    mime_type = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    file_name = db.Column(db.String(200), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)        # تاريخ انتهاء الصلاحية (من ميتا)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_media_id', 'media_id'),
        db.Index('idx_media_expires', 'expires_at'),
    )
