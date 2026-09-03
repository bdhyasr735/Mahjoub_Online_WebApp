# coding: utf-8
# 📂 config.py
import os

class Config:
    # 🗝️ مفاتيح الحماية والأمان الأساسية
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key_mahjoub_online')
    
    # 🔄 إجبار Flask على إعادة تحميل القوالب وإلغاء تخزين الكاش للملفات
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0
    
    # 🗄️ إعدادات قاعدة البيانات (PostgreSQL / SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🔌 حماية محرك الاتصال وإجبار SSL لمنع انقطاع الاتصال مع Render / PostgreSQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_timeout": 30,
        "connect_args": {
            "sslmode": "require"  # 👈 إضافة هذا السطر لحل استثناء SSL Closed Unexpectedly
        }
    }

    # 🛡️ إعدادات حماية CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # ============================================================
    # 📧 إعدادات البريد الإلكتروني (Flask-Mail)
    # ============================================================
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@mahjoub.online')
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'true').lower() == 'true'

    # ============================================================
    # 💬 إعدادات API الخاصة بـ Meta WhatsApp
    # ============================================================
    WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN', '')
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')
    WHATSAPP_BUSINESS_ACCOUNT_ID = os.environ.get('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
    WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token')
    WHATSAPP_API_VERSION = os.environ.get('WHATSAPP_API_VERSION', 'v20.0')

    # ============================================================
    # 🖼️ إعدادات Cloudinary (لتخزين الصور والملفات)
    # ============================================================
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', 'tpziz28b')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '397386914561283')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', 'j6XFUVjUt9xsHSYwJ2BgnSaVfX8')

    @staticmethod
    def validate_config():
        """التحقق من صحة المتغيرات الأساسية عند التشغيل لضمان عدم وجود نقص حرج"""
        missing = []
        warnings = []
        
        # ✅ متغيرات إلزامية
        if not Config.SECRET_KEY or Config.SECRET_KEY == 'default_secret_key_mahjoub_online':
            missing.append('SECRET_KEY')
        
        # ⚠️ متغيرات اختيارية (تحذير فقط)
        if not Config.WHATSAPP_ACCESS_TOKEN:
            warnings.append('WHATSAPP_ACCESS_TOKEN (WhatsApp معطل)')
        if not Config.WHATSAPP_PHONE_NUMBER_ID:
            warnings.append('WHATSAPP_PHONE_NUMBER_ID (WhatsApp معطل)')
        
        # 📧 البريد الإلكتروني اختياري في التطوير
        if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
            if Config.MAIL_SUPPRESS_SEND:
                warnings.append('MAIL_USERNAME/MAIL_PASSWORD (البريد معطل في وضع التطوير)')
            else:
                warnings.append('MAIL_USERNAME/MAIL_PASSWORD (البريد غير مهيأ للإنتاج)')
        
        if missing:
            print(f"❌ [Config Error]: متغيرات إلزامية مفقودة: {', '.join(missing)}")
            return False
        
        if warnings:
            print(f"⚠️ [Config Warning]: {', '.join(warnings)}")
        else:
            print("✅ [Config]: تم التحقق من سلامة إعدادات التكوين بنجاح.")
        
        return True

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SUPPRESS_SEND = True
    PRINT_OTP_TO_CONSOLE = True

class ProductionConfig(Config):
    DEBUG = False
    MAIL_SUPPRESS_SEND = False
    PRINT_OTP_TO_CONSOLE = False
