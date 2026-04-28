import os
from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# 1. تعريف الكائنات الأساسية للنظام (Globally)
# ملاحظة: نتركها هنا فارغة ليتم ربطها داخل create_app لاحقاً
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # 2. جلب الإعدادات من ملف config.py
    try:
        from config import Config
        app.config.from_object(Config)
    except ImportError:
        # إعدادات طوارئ في حال فقدان ملف التكوين
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mahjoub_online.db'
        app.config['SECRET_KEY'] = 'mahjoub-secret-key-123'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 3. تهيئة الإضافات وربطها بالتطبيق فعلياً
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # 4. إعدادات إدارة الدخول والوصول السيادي
    login_manager.login_view = 'admin_panel.admin_login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى النظام السيادي."
    login_manager.login_message_category = "info"

    @login_manager.unauthorized_handler
    def unauthorized():
        # التوجيه التلقائي لبرج الرقابة عند محاولة الوصول غير المصرح به
        return redirect(url_for('admin_panel.admin_login'))

    with app.app_context():
        # 5. استيراد الموديلات داخل السياق لضمان ربط الجداول
        from core.models.user import User
        from core.models.product import Product
        from core.models.supplier import Supplier
        
        # 6. تسجيل بوابة الموردين (Supplier Panel)
        # تم وضع الاستيراد هنا لحل مشكلة Circular Import وخطأ "cannot import name app"
        try:
            from supplier_panel.routes import supplier_bp
            if 'supplier_panel' not in app.blueprints:
                app.register_blueprint(supplier_bp, url_prefix='/supplier')
                print("✅ تم تفعيل بوابة الموردين بنجاح")
        except Exception as e:
            print(f"⚠️ تنبيه: بوابة الموردين لم تفعل بعد: {e}")

        # 7. تسجيل بوابة الإدارة (Admin Panel - برج الرقابة 🏛️)
        try:
            from admin_panel.routes import admin_bp 
            if 'admin_panel' not in app.blueprints:
                app.register_blueprint(admin_bp, url_prefix='/admin')
                print("✅ تم تفعيل برج الرقابة المركزية بنجاح")
        except Exception as e:
            print(f"⚠️ خطأ في بوابة الإدارة: {e}")

        # 8. إنشاء الجداول (في حال عدم وجود قاعدة البيانات)
        db.create_all()

    # 9. إرجاع كائن التطبيق (المحرك الرئيسي)
    return app

# 10. محمل المستخدم (User Loader)
@login_manager.user_loader
def load_user(user_id):
    from core.models.user import User
    try:
        # الطريقة الآمنة لجلب الهوية السيادية للمستخدم
        return db.session.get(User, int(user_id))
    except Exception as e:
        print(f"❌ خطأ في نظام التحقق من الهوية: {e}")
        return None
