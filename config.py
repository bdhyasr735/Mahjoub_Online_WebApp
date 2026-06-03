# coding: utf-8
# ⚙️ مهندس الإعدادات المركزية السحابية - منصة محجوب أونلاين 2026

import os

class Config:
    # 🛡️ مفتاح الأمان السيادي للمنصة
    SECRET_KEY = os.environ.get('SECRET_KEY', 'SOVEREIGN_KEY_2026')
    
    # 🔒 إعدادات الحماية الأمنية للـ Cookies (لرفع تقييم الأمان)
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 1. جلب رابط قاعدة البيانات السحابية
    _db_url = os.environ.get('DATABASE_URL')
    
    # 2. ⚡ إصلاح بادئة الرابط تلقائياً
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
    QUMRA_API_KEY = os.environ.get('QUMRA_API_KEY')
    QUMRA_API_URL = os.environ.get('QUMRA_API_URL')

    # 7. إعدادات WhatsApp Cloud API
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '1190456080809834')
    
    # رمز الوصول الدائم
    WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN', 'EAAMcZAOecIhEBRsQYN0b4K9tumryxfm0thi25Xb0v1n7sEF6ZAQk8zAWBZAtLMh8T8U03PPQbZAm17hUChh2qhIDPxOOsL0ZAYuZBKy7esEp5yPZC9rc6Yp3AZBbDefmntxixSmHOxSA9DVlzD2kCvWjZCpiZCogYw29llYyACoMUXY6jawwGW1dz7BfWTBFTekw1wSe4KfhCCJkJnSnY0sB9SwG4k7UeBY8TZASI2R2Jig67eBgbCNZB85Wnazqs9HuZBZAW3wfpwlqNY0bwsZA2rAByGOAmsFJLUZD')
    
    WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'Mahjoub_WhatsApp_Secure_2026')

    # 8. الحفاظ على ترميز ونقاء النصوص والبيانات باللغة العربية
    JSON_AS_ASCII = False
