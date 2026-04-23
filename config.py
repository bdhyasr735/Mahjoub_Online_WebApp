import os

class Config:
    # جلب رابط قاعدة البيانات من رويال
    db_url = os.environ.get('DATABASE_URL')
    
    # تصحيح الرابط برمجياً (حل مشكلة postgres://)
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # إعدادات قمرة (المفاتيح التي ظهرت في صورتك)
    QUMRA_API_URL = os.environ.get('QUMRA_API_URL')
    QUMRA_API_KEY = os.environ.get('QUMRA_API_KEY')
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mahjoub_2026_top_secret')
