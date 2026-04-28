import os
from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# 1. تعريف الكائنات الأساسية للنظام (Globally)
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # 2. جلب الإعدادات (دعم كامل لبيئة Railway)
    try:
        from config import Config
        app.config.from_object(Config)
    except ImportError:
        # إعدادات افتراضية في حال عدم وجود ملف config
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///mahjoub_online.db'
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'mahjoub-secret-key-123'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 3. تهيئة الإضافات وربطها بالتطبيق
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # 4. إعدادات إدارة الدخول السيادي
    login_manager.login_view = 'admin_panel.admin_login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى النظام السيادي."
    login_manager.login_message_category = "info"

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for('admin_panel.admin_login'))

    with app.app_context():
        # 5. استيراد الموديلات لضمان بناء الجداول
        from core.models.user import User
        from core.models.product import Product
        from core.models.supplier import Supplier
        
        # 6. تسجيل بوابة الموردين (Supplier Panel)
        # الاستيراد داخل السياق يحل مشكلة "cannot import name app"
        try:
            from supplier_panel.routes import supplier_bp
            if 'supplier_panel' not in app.blueprints:
                app.register_blueprint(supplier_bp, url_prefix='/supplier')
                print("✅ تم تفعيل بوابة الموردين بنجاح")
        except Exception as e:
            # هذا التنبيه سيختفي بمجرد تعديل الاستيراد في routes.py
            print(f"⚠️ تنبيه: بوابة الموردين لم تفعل بعد: {e}")

        # 7. تسجيل بوابة الإدارة (برج الرقابة 🏛️)
        try:
            from admin_panel.routes import admin_bp 
            if 'admin_panel' not in app.blueprints:
                app.register_blueprint(admin_bp, url_prefix='/admin')
                print("✅ تم تفعيل برج الرقابة المركزية بنجاح")
        except Exception as e:
            print(f"⚠️ خطأ في بوابة الإدارة: {e}")

        # 8. إنشاء الجداول وتعميد الحساب الأول
        db.create_all()

        # الخطوة الحاسمة: تعميد حساب "محجوب أونلاين"
        # تم التأكد من مطابقة الحقول لملف core/models/user.py
        if not User.query.filter_by(username="محجوب أونلاين").first():
            print("🚀 جاري تعميد حساب المورد الأول...")
            try:
                sys_supplier = User(
                    username="محجوب أونلاين", 
                    role="supplier", 
                    status="approved"  # هذا الحقل أصبح مفعلاً الآن بعد تعديلك للموديل
                )
                sys_supplier.set_password("123")
                db.session.add(sys_supplier)
                db.session.commit()
                print("✨ تم إنشاء حساب المورد بنجاح")
            except Exception as e:
                db.session.rollback()
                print(f"❌ فشل تعميد الحساب: {e}")

    return app

# 9. محمل المستخدم
@login_manager.user_loader
def load_user(user_id):
    from core.models.user import User
    try:
        return db.session.get(User, int(user_id))
    except Exception as e:
        print(f"❌ خطأ في نظام التحقق من الهوية: {e}")
        return None
