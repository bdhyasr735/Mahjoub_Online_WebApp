import os
from dotenv import load_dotenv

# تحميل ملف .env للعمل محلياً
load_dotenv()

class Config:
    # 1. إعدادات قاعدة البيانات السيادية
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # تصحيح البروتوكول ليتوافق مع SQLAlchemy الحديثة (مثل Render/Railway)
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        # إضافة sslmode للاتصال الآمن بالسحابة إذا لم يكن موجوداً
        if "postgresql" in database_url and "sslmode=" not in database_url:
            separator = "&" if "?" in database_url else "?"
            database_url += f"{separator}sslmode=require"
        
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # في حال عدم وجود DATABASE_URL، سننشئ قاعدة بيانات جديدة باسم v2 لضمان عدم التضارب
        # يمكنك تغيير الاسم لاحقاً أو حذف الملف القديم يدوياً
        SQLALCHEMY_DATABASE_URI = 'sqlite:///mahjoub_online_v2.db'
                
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 2. إعدادات "قمرة" (Qumra) المستدعاة في qumra_handler
    QUMRA_API_KEY = os.environ.get('QUMRA_API_KEY')
    QUMRA_API_URL = os.environ.get('QUMRA_API_URL')
    
    # 3. حماية الجلسات والبيانات
    SECRET_KEY = os.environ.get('SECRET_KEY', 'MAHJOUB_ONLINE_SECURE_2026')
    
    # 4. إعدادات استقرار الجلسات (بما يتوافق مع بيئات الاستضافة الحديثة)
    # ملاحظة: إذا كنت تختبر محلياً بدون HTTPS، اجعل SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True') == 'True'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PREFERRED_URL_SCHEME = 'https'
    REMEMBER_COOKIE_DURATION = 3600 * 24 * 7 # تذكر الدخول لمدة أسبوع
