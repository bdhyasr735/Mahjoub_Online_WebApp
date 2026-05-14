# coding: utf-8
# ملف التشغيل الرئيسي - متوافق مع إعدادات PYTHONPATH=.
import os
import sys

# 🚀 بما أنك أضفت المسار في الإعدادات، سنقوم بتأكيد ذلك برمجياً أيضاً
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from flask import Flask

# الاستيراد المباشر من الحزمة models
try:
    from models.admin_db import db, AdminUser
    print("✅ تم العثور على النماذج بنجاح باستخدام PYTHONPATH")
except ImportError as e:
    print(f"❌ لا يزال هناك خطأ في المسار: {e}")
    db = None
    AdminUser = None

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_key_2026')
    
    if db:
        db.init_app(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run()
