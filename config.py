# config.py
# coding: utf-8
# ⚙️ مهندس الإعدادات المركزية - منصة محجوب أونلاين 2026

import os

class Config:
    # مفتاح الأمان السيادي للمنصة (يُجلب من متغيرات البيئة في Vercel)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'SOVEREIGN_KEY_2026')
    
    # 1. جلب رابط قاعدة البيانات
    db_url = os.environ.get('DATABASE_URL')
    
    # 2. 🛡️ إصلاح بادئة الرابط ليتوافق مع SQLAlchemy الحديثة (مهم جداً لـ PostgreSQL)
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    # 3. إسناد الرابط المصحح أو استخدام SQLite محلي للتطوير
    SQLALCHEMY_DATABASE_URI = db_url or 'sqlite:///mahjoub_online.db'
    
    # 4. تعطيل تتبع التعديلات (لتحسين استهلاك الذاكرة في السحابة)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 5. إعدادات API الخارجية (يتم جلبها من لوحة تحكم Vercel)
    QUMRA_API_KEY = os.environ.get('QUMRA_API_KEY')
    QUMRA_API_URL = os.environ.get('QUMRA_API_URL')

    # 6. إعداد إضافي لتحسين التعامل مع السيرفرات السحابية
    JSON_AS_ASCII = False
