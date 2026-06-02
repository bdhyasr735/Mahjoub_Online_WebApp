# config.py
# coding: utf-8
# ⚙️ مهندس الإعدادات المركزية السحابية - منصة محجوب أونلاين 2026

import os

class Config:
    # 🛡️ مفتاح الأمان السيادي للمنصة (يُجلب من متغيرات البيئة في Vercel)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'SOVEREIGN_KEY_2026')
    
    # 1. جلب رابط قاعدة البيانات السحابية (Supabase) المضاف في Vercel
    db_url = os.environ.get('DATABASE_URL')
    
    # 2. ⚡ إصلاح بادئة الرابط ليتوافق مع SQLAlchemy الحديثة (مهم لـ PostgreSQL)
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    # 3. إسناد الرابط المصحح أو استخدام SQLite محلي للتطوير الاحتياطي
    SQLALCHEMY_DATABASE_URI = db_url or 'sqlite:///mahjoub_online.db'
    
    # 4. ❌ تعطيل تتبع التعديلات (لتحسين استهلاك الذاكرة في السحابة)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 5. 💎 حوكمة وإدارة الاتصالات لبيئات الـ Serverless (إلزامي لـ Supabase)
    # تمنع هذه الإعدادات بقاء الاتصالات مفتوحة وميتة مما يحمي خادم قاعدة البيانات من الانهيار
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,             # الحد الأقصى للاتصالات الدائمة
        "max_overflow": 20,          # الاتصالات الإضافية المسموح بها عند الضغط المكثف
        "pool_recycle": 1800,        # إعادة تدوير الاتصال كل 30 دقيقة لتجنب قطعه من جهة السيرفر
        "pool_pre_ping": True        # فحص سلامة الاتصال قبل إرسال الاستعلامات لتجنب خطأ الـ 500
    }
    
    # 6. إعدادات API الخارجية (يتم جلبها من لوحة تحكم Vercel)
    QUMRA_API_KEY = os.environ.get('QUMRA_API_KEY')
    QUMRA_API_URL = os.environ.get('QUMRA_API_URL')

    # 7. الحفاظ على ترميز اللغة العربية الأصيل في استجابات الـ JSON
    JSON_AS_ASCII = False
