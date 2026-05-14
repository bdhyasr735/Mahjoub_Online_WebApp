# coding: utf-8
# 🌟 استيراد المكتبات الأساسية
import os
from flask import Flask, redirect, url_for
from models.admin_db import db

def create_app():
    """
    دالة إنشاء التطبيق: تقوم بتجميع أجزاء المنصة وتجهيز محرك Jinja2 للقوالب.
    """
    # 📁 تعيين مجلد القوالب (Jinja2) - تأكد من وجوده في المسار المحدد
    app = Flask(__name__, template_folder='apps/templates')
    
    # 🔐 مفتاح الأمان لإدارة الجلسات وتأمين البيانات
    app.secret_key = os.environ.get('SECRET_KEY') or 'MAHJOUB_SECURE_2026'

    # 🗄️ تهيئة رابط قاعدة البيانات (PostgreSQL لمنصة Railway)
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        # تصحيح البروتوكول ليتوافق مع مكتبة SQLAlchemy
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mahjoub_admin.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 🔗 ربط كائن قاعدة البيانات بالتطبيق
    db.init_app(app)

    # 🚀 تسجيل الروابط (Blueprints) - تأكد من صحة مسارات الملفات لديك
    try:
        from apps.auth_portal.routes import auth_bp
        from apps.admin_dashboard.routes import admin_dashboard  
        from apps.add_supplier.routes import admin_suppliers

        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(admin_dashboard, url_prefix='/admin')
        app.register_blueprint(admin_suppliers, url_prefix='/admin/suppliers')
    except ImportError as e:
        print(f"⚠️ خطأ في استيراد الروابط: {e}")

    # 🛠️ إنشاء الجداول في قاعدة البيانات عند أول تشغيل
    with app.app_context():
        db.create_all()

    # 🏠 التوجيه التلقائي لصفحة تسجيل الدخول
    @app.route('/')
    def root():
        return redirect(url_for('auth_portal.login')) 

    return app

# 🔑 المتغير 'app' هو ما يبحث عنه Gunicorn في الصورة image_78a7f2.png
app = create_app()

if __name__ == '__main__':
    # 🔌 تشغيل التطبيق على المنفذ المخصص من Railway
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
