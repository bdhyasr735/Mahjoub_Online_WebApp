# 📂 config.py
import os

class Config:
    # 🗝️ مفاتيح الحماية والأمان الأساسية
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key_mahjoub_online')
    
    # 🗄️ إعدادات قاعدة البيانات (PostgreSQL / SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🛡️ إعدادات حماية CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # 💬 إعدادات API الخاصة بـ Meta WhatsApp
    WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
    WHATSAPP_API_VERSION = os.environ.get('WHATSAPP_API_VERSION', 'v20.0')

    @staticmethod
    def validate_config():
        """التحقق من صحة المتغيرات الأساسية عند التشغيل لضمان عدم وجود نقص حرج"""
        missing = []
        if not Config.SECRET_KEY:
            missing.append('SECRET_KEY')
        
        if missing:
            print(f"⚠️ [Config Warning]: متغيرات البيئة التالية مفقودة: {', '.join(missing)}")
        else:
            print("✅ [Config]: تم التحقق من سلامة إعدادات التكوين بنجاح.")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# ⚠️ لا يوجد أي استيراد لـ create_app أو لموديول apps هنا إطلاقاً لقطع الـ Circular Import
