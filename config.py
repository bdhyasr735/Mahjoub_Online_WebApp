# coding: utf-8
# ⚙️ مهندس الإعدادات المركزية السحابية - منصة محجوب أونلاين 2026

import os

class Config:
    """إعدادات النظام المركزية مع حماية للبيانات الحساسة."""
    
    # 🛡️ مفتاح الأمان السيادي للمنصة
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # 🔐 مفتاح التشفير المركزي (لـ AES-256)
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    
    # 🕵️‍♂️ مفتاح توقيع الويب هوك (للتحقق من مصدر الطلبات)
    WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')
    
    # 🌐 رابط المتجر الأساسي
    STORE_BASE_URL = os.environ.get('STORE_BASE_URL', 'https://mahjoub.online')
    
    # 🔒 إعدادات الحماية الأمنية للـ Cookies
    IS_PRODUCTION = os.environ.get('ENV', 'production') == 'production'
    SESSION_COOKIE_SECURE = IS_PRODUCTION 
    REMEMBER_COOKIE_SECURE = IS_PRODUCTION
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 1. إعدادات قاعدة البيانات (مع التحقق من التوافق)
    _db_url = os.environ.get('DATABASE_URL')
    if _db_url and _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql+psycopg2://", 1)
        
    SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///mahjoub_online.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 2. إعدادات Pool الاتصالات (لأداء سحابي مستقر)
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
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
    WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN')

    # 5. إعدادات HyperSender
    HYPERSEND_API_KEY = os.environ.get('HYPERSEND_API_KEY')
    HYPERSEND_INSTANCE_ID = os.environ.get('HYPERSEND_INSTANCE_ID')

    # 6. إعدادات المزامنة
    SYNC_MODE = os.environ.get('SYNC_MODE', 'live')

    # 7. ترميز النصوص
    JSON_AS_ASCII = False

    @classmethod
    def validate_config(cls):
        """التحقق من وجود المفاتيح الحساسة في بيئة الإنتاج."""
        if cls.IS_PRODUCTION:
            required = ['SECRET_KEY', 'ENCRYPTION_KEY', 'WEBHOOK_SECRET', 'QUMRA_API_KEY']
            for var in required:
                if not getattr(cls, var):
                    raise EnvironmentError(f"❌ المتغير الحساس {var} مفقود في بيئة الإنتاج!")
        return True
