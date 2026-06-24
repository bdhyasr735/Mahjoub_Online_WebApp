# coding: utf-8
# ⚙️ مهندس الإعدادات المركزية السحابية - منصة محجوب أونلاين 2026

import os

class Config:
    # 🛡️ مفتاح الأمان السيادي للمنصة
    SECRET_KEY = os.environ.get('SECRET_KEY', 'SOVEREIGN_KEY_2026')
    
    # 🔐 مفتاح التشفير المركزي (لـ AES-256) 
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=')
    
    # 🕵️‍♂️ مفتاح توقيع الويب هوك الجديد
    WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'cdde0d415221df2c074cc80d226b6ef1ab9b5ef1f24f9c1a37aec40f2d9df2a7')
    
    # 🌐 رابط المتجر الأساسي
    STORE_BASE_URL = os.environ.get('STORE_BASE_URL', 'https://mahjoub.online')
    
    # 🔒 إعدادات الحماية الأمنية للـ Cookies
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 1. إعدادات قاعدة البيانات
    _db_url = os.environ.get('DATABASE_URL')
    if _db_url:
        if _db_url.startswith("postgres://"):
            _db_url = _db_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif _db_url.startswith("postgresql://"):
            _db_url = _db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///mahjoub_online.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 2. إعدادات Pool الاتصالات
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 15,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True
    }
    
    # 3. إعدادات Qumra Cloud API
    QUMRA_API_KEY = os.environ.get('QUMRA_API_KEY')
    QUMRA_API_URL = os.environ.get('QUMRA_API_URL', 'https://mahjoub.online/admin/graphql')

    # 4. إعدادات WhatsApp Cloud API
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '1190456080809834')
    WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN', 'rb3tZFnHRcsN')
    WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'Mahjoub_WhatsApp_Secure_2026')

    # 5. إعدادات HyperSender (للتحقق السيادي عبر OTP)
    HYPERSEND_API_KEY = os.environ.get('HYPERSEND_API_KEY')
    HYPERSEND_INSTANCE_ID = os.environ.get('HYPERSEND_INSTANCE_ID')

    # 6. ترميز النصوص
    JSON_AS_ASCII = False
