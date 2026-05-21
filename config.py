# config.py
# coding: utf-8
# ⚙️ مهندس الإعدادات المركزية - منصة محجوب أونلاين 2026

import os

class Config:
    # مفتاح الأمان السيادي للمنصة
    SECRET_KEY = os.environ.get('SECRET_KEY', 'SOVEREIGN_KEY_2026')
    
    # 1. جلب رابط قاعدة البيانات
    db_url = os.environ.get('DATABASE_URL')
    
    # 2. 🛡️ إصلاح بادئة الرابط ليتوافق مع SQLAlchemy الحديثة
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    # 3. إسناد الرابط المصحح
    SQLALCHEMY_DATABASE_URI = db_url or 'sqlite:///mahjoub_fallback.db'
    
    # إيقاف تتبع التعديلات لرفع الأداء
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 🛡️ إعدادات المح
