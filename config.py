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

    # 🔌 حماية محرك الاتصال من انقطاع SSL وإعادة الاتصال تلقائياً
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_timeout": 30,
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
        if not Config.SECRET_KEY or Config.SECRET_KEY == 'default_secret_key_mahjoub_online':
            missing.append('SECRET_KEY')
        if not Config.WHATSAPP_ACCESS_TOKEN:
            missing.append('WHATSAPP_ACCESS_TOKEN')
        if not Config.WHATSAPP_PHONE_NUMBER_ID:
            missing.append('WHATSAPP_PHONE_NUMBER_ID')
        if not Config.MAIL_USERNAME:
            missing.append('MAIL_USERNAME')
        if not Config.MAIL_PASSWORD:
            missing.append('MAIL_PASSWORD')
        
        if missing:
            print(f"⚠️ [Config Warning]: متغيرات البيئة التالية مفقودة أو غير آمنة: {', '.join(missing)}")
        else:
            print("✅ [Config]: تم التحقق من سلامة إعدادات التكوين بنجاح.")

class DevelopmentConfig(Config):
    DEBUG = True
    # في بيئة التطوير، يمكن استخدام بريد وهمي
    MAIL_SUPPRESS_SEND = True

class ProductionConfig(Config):
    DEBUG = False
    MAIL_SUPPRESS_SEND = False

# ⚠️ لا يوجد أي استيراد لـ create_app أو لموديول apps هنا إطلاقاً لقطع الـ Circular Import
