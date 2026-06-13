# coding: utf-8
# ⚙️ مهندس الإعدادات المركزية السحابية - منصة محجوب أونلاين 2026

import os

class Config:
    # 🛡️ مفتاح الأمان السيادي للمنصة
    SECRET_KEY = os.environ.get('SECRET_KEY', 'SOVEREIGN_KEY_2026')
    
    # 🔐 مفتاح التشفير المركزي (لـ AES-256) 
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=')
    
    # 🔒 إعدادات الحماية الأمنية للـ Cookies
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 1. جلب رابط قاعدة البيانات السحابية
    _db_url = os.environ.get('DATABASE_URL')
    
    # 2. ⚡ إصلاح بادئة الرابط تلقائياً ليتوافق مع SQLAlchemy
    if _db_url:
        if _db_url.startswith("postgres://"):
            _db_url = _db_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif _db_url.startswith("postgresql://"):
            _db_url = _db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        
    # 3. إسناد الرابط المصحح
    SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///mahjoub_online.db'
    
    # 4. ❌ تعطيل تتبع التعديلات
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 5. 💎 حوكمة وإدارة الاتصالات لبيئة Render
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 15,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True
    }
    
    # 6. إعدادات البنية التحتية السحابية (Qomra Cloud API)
    # ملاحظة: تم جلب المفتاح من المتغيرات البيئية حصراً
    QUMRA_API_KEY = os.environ.get('QUMRA_API_KEY')
    QUMRA_API_URL = os.environ.get('QUMRA_API_URL', 'https://mahjoub.online/admin/graphql')

    # 7. إعدادات WhatsApp Cloud API
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '1190456080809834')
    WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN', None)
    WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'Mahjoub_WhatsApp_Secure_2026')

    # 8. الحفاظ على ترميز ونقاء النصوص والبيانات باللغة العربية
    JSON_AS_ASCII = False
