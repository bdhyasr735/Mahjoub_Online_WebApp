# core/__init__.py
import random
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# تعريف المحركات الأساسية للترسانة الرقمية (العمود الفقري)
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # --- 1. إعدادات السيادة ---
    # ملاحظة: يفضل جلب DATABASE_URL من متغيرات البيئة في Railway
    app.config['SECRET_KEY'] = 'mahjoub_sovereign_secret_2026'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://...' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- 2. تفعيل المحركات ---
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # إعدادات حوكمة الدخول
    login_manager.login_view = 'admin.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى الترسانة السيادية"
    login_manager.login_message_category = "info"

    with app.app_context():
        # --- 3. استيراد النماذج (Models) لضمان تسجيلها في SQLAlchemy ---
        from core.models.user import User
        from core.models.vendor import Vendor
        
        # 🛡️ تصحيح الترسانة: محاولة إنشاء الجداول المفقودة تلقائياً
        try:
            db.create_all()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ تنبيه: تعذر تحديث الهيكل تلقائياً: {e}")

        # --- 4. المعالجات السياقية (Global Context Processors) ---
        @app.context_processor
        def utility_processor():
            def get_sovereign_data():
                """توليد المعرف MAH-963 والمحفظة بشكل آلي لجميع القوالب"""
                base_prefix = "MAH-963"
                try:
                    # حساب عدد الموردين لضمان تسلسل الهوية السيادية
                    count = db.session.query(Vendor.id).count() if Vendor else 0
                    next_num = count + 1
                    final_serial = f"{base_prefix}{next_num}"
                    return {
                        "id": final_serial,
                        "wallet": f"W-{final_serial}"
                    }
                except Exception:
                    db.session.rollback()
                    rand_id = random.randint(100, 999)
                    return {"id": f"{base_prefix}{rand_id}", "wallet": f"W-{base_prefix}{rand_id}"}

            sov_data = get_sovereign_data()
            return dict(next_id=sov_data['id'], next_wallet=sov_data['wallet'])

        # --- 5. تسجيل الـ Blueprints (مركز القيادة) ---
        # يتم الاستيراد هنا حصراً لمنع خطأ ImportError الملاحظ في سجلات Railway
        from admin_panel import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

# --- 6. إدارة جلسات المستخدمين ---
@login_manager.user_loader
def load_user(user_id):
    from core.models.user import User
    try:
        return User.query.get(int(user_id))
    except Exception:
        db.session.rollback()
        return None
