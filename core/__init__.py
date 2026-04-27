import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 1. تعريف الكائنات الأساسية خارج الدالة لسهولة الوصول إليها
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # 2. إنشاء كائن التطبيق
    app = Flask(__name__)

    # 3. الإعدادات السيادية (Configurations)
    # ملاحظة: تأكد من ضبط SECRET_KEY في إعدادات Railway
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mahjoub_online_9046_sovereign_key')
    
    # ربط قاعدة البيانات (PostgreSQL في Railway أو SQLite محلياً)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///mahjoub_online.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 4. تهيئة الإضافات مع التطبيق
    db.init_app(app)
    login_manager.init_app(app)

    # إعدادات نظام الدخول
    login_manager.login_view = 'supplier_panel.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى الترسانة."
    login_manager.login_message_category = "info"

    # 5. تسجيل البوابات (Blueprints) داخل سياق التطبيق
    with app.app_context():
        # استيراد النماذج (Models) لضمان إنشاء الجداول
        from core import models
        
        # استيراد وتسجيل بوابة الموردين (التسجيل يتم هنا فقط!)
        from supplier_panel import supplier_bp
        app.register_blueprint(supplier_bp, url_prefix='/supplier')

        # إنشاء الجداول السيادية إذا لم تكن موجودة
        db.create_all()

    return app

# 6. إنشاء نسخة التطبيق النهائية للتشغيل (Gunicorn سيبحث عن هذه النسخة)
app = create_app()

@login_manager.user_loader
def load_user(user_id):
    from core.models import User
    return User.query.get(int(user_id))
