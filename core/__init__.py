# core/__init__.py
import os
from flask import Flask
from flask_login import LoginManager

# استيراد db من ملف extensions لضمان عدم حدوث استيراد دائري (Circular Import)
from .extensions import db

# تهيئة مدير الدخول
login_manager = LoginManager()

def create_app():
    # إنشاء تطبيق Flask مع تحديد مسارات المجلدات الثابتة والقوالب بدقة
    app = Flask(__name__, 
                static_folder='../static', 
                template_folder='../templates')
    
    # تحميل الإعدادات (تأكد من وجود ملف config.py في المجلد الرئيسي)
    app.config.from_object('config.Config')
    
    # 2. ربط قاعدة البيانات ونظام الدخول بالتطبيق
    db.init_app(app)
    login_manager.init_app(app)

    # إعدادات حماية الجلسة السيادية
    login_manager.login_view = 'admin.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى منطقة الإدارة السيادية."
    login_manager.login_message_category = "info"

    with app.app_context():
        # --- 3. استيراد الموديلات (استخدام الاستيراد النسبي لضمان التوافق مع Railway) ---
        from .models.user import User
        from .models.supplier import Supplier 
        from .models.product import Product
        from .models.business import Order

        # --- 4. تسجيل الـ Blueprints ---
        # ملاحظة: إذا كان admin_panel مجلداً بجانب core، نستخدم الاستيراد المطلق
        try:
            from admin_panel import admin_bp
            app.register_blueprint(admin_bp, url_prefix='/admin')
        except ImportError:
            print("⚠️ تنبيه: لم يتم العثور على Blueprint 'admin_panel' - تأكد من وجود المجلد.")

        # --- 5. محمل المستخدم (User Loader) ---
        @login_manager.user_loader
        def load_user(user_id):
            # نستخدم .get() للبحث عن المستخدم في القاعدة
            return User.query.get(int(user_id))

    return app
