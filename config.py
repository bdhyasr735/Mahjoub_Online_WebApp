import os

class Config:
    # جلب الرابط من Railway Variables
    raw_uri = os.environ.get('DATABASE_URL')
    
    # تصحيح البروتوكول إذا كان يبدأ بـ postgres://
    if raw_uri and raw_uri.startswith("postgres://"):
        raw_uri = raw_uri.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = raw_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mahjoub_secret_2026')
    
    # إعدادات قمرة
    QUMRA_API_URL = os.environ.get('QUMRA_API_URL')
    QUMRA_API_KEY = os.environ.get('QUMRA_API_KEY')
