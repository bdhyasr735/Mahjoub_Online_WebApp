# coding: utf-8
# 📂 apps/models/admin_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from apps.extensions import db

class AdminUser(db.Model, UserMixin):
    """موديل إدارة النظام: مع تشفير سيادي وفهرسة أداء متقدمة."""
    __tablename__ = 'admin_users'
    
    # [فهرسة الأداء]: تحسين سرعة الاستعلامات والبحث
    __table_args__ = (
        db.Index('idx_adm_username', 'username'),
        db.Index('idx_adm_role', 'role'),
        db.Index('idx_adm_phone', 'search_phone'), 
        db.Index('idx_adm_created', 'created_at'),
        {'extend_existing': True}
    )
    
    # 1. الحقول الأساسية
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 2. معلومات الحساب - [نظام تشفير AES-256 السيادي]
    role = db.Column(db.String(20), default='Owner')
    is_active = db.Column(db.Boolean, default=True)
    _phone_enc = db.Column(db.String(255), nullable=True) 
    search_phone = db.Column(db.String(20)) 
    
    # 3. التدقيق الزمني
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # 4. أمثلة للعلاقات (مع التحميل الكسول - Lazy Loading)
    # ملاحظة: إذا قمت بإضافة علاقات لاحقاً، استخدم دائماً lazy='select' 
    # لضمان عدم جلب البيانات إلا عند الحاجة الفعلية.
    # مثال:
    # activity_logs = db.relationship('ActivityLog', backref='admin', lazy='select')

    # --- نظام التشفير الاحترافي (Fernet / AES-256) ---
    @staticmethod
    def _get_key():
        """استرجاع المفتاح السيادي من متغيرات البيئة."""
        return os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=').encode()

    @property
    def phone(self):
        """فك التشفير عند العرض."""
        if not self._phone_enc: return None
        try:
            return Fernet(self._get_key()).decrypt(self._phone_enc.encode()).decode()
        except Exception: 
            return None

    @phone.setter
    def phone(self, value):
        """تشفير الهاتف قبل التخزين مع الاحتفاظ بـ search_phone للبحث."""
        if value:
            # تشفير القيمة كاملة
            self._phone_enc = Fernet(self._get_key()).encrypt(str(value).encode()).decode()
            # الاحتفاظ بآخر 9 أرقام للفهرسة (Index)
            self.search_phone = str(value)[-9:] 

    # --- نظام تأمين كلمة المرور (PBKDF2) ---
    def set_password(self, password):
        """توليد Hash مشفر بـ SHA256 للكلمة المرور."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """التحقق من صحة كلمة المرور المدخلة."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminUser {self.username}>'
