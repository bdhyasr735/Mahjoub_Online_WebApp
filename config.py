import os
from dotenv import load_dotenv

# تحميل ملف .env إذا كان موجوداً (للعمل محلياً)
load_dotenv()

class Config:
    # 1. إعدادات قاعدة البيانات (ريندر)
    database_url = os.environ.get('DATABASE_URL')
    
    # تصحيح الرابط ليتوافق مع SQLAlchemy 3.x وإضافة SSL
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        # التأكد من وجود sslmode إذا لم يكن موجوداً في الرابط الأصلي
        if "sslmode=" not in database_url:
            if "?" in database_url:
                database_url += "&sslmode=require"
            else:
                database_url += "?sslmode=require"
                
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 2. إعدادات "قمرة" (Qumra)
    QUMRA_API_KEY = os.environ.get('QUMRA_API_KEY')
    QUMRA_API_URL = os.environ.get('QUMRA_API_URL')
    
    # 3. مفتاح الأمان للتطبيق
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key_123')
