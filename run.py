# coding: utf-8
# ملف: run.py
import os
import sys

# 🚀 تعليم بايثون مكان المجلدات لضمان عدم حدوث ImportError
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from flask import Flask

# استيراد النماذج من المجلد الذي يحتوي على __init__.py
try:
    from models.admin_db import db, AdminUser
    print("✅ تم التعرف على AdminUser بنجاح")
except ImportError as e:
    print(f"❌ خطأ حرج في الاستيراد: {e}")
    # تعريفات وهمية لمنع gunicorn من الانهيار فوراً
    db = None
    AdminUser = None

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_key_2026')
    
    if db:
        db.init_app(app)
        with app.app_context():
            try:
                db.create_all()
            except Exception as db_err:
                print(f"⚠️ فشل تحديث جداول القاعدة: {db_err}")
                
    return app

# الكائن المطلوب لتشغيل الخادم (web: gunicorn run:app)
app = create_app()

if __name__ == "__main__":
    app.run()
