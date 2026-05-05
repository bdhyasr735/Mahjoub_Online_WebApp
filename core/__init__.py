import re
import random
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# إنشاء كائنات النظام الأساسية (العمود الفقري للترسانة الرقمية)
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- 1. إعدادات الأمان والتواصل (CORS) ---
    @app.after_request
    def add_cors_headers(response):
        """السماح بالتواصل السيادي الآمن بين أنظمة المنصة الموزعة"""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

    # --- 2. تهيئة المحركات الأساسية ---
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # حوكمة الدخول وتوجيه غير المصرح لهم إلى لوحة الإدارة
    login_manager.login_view = 'admin.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى النظام السيادي."
    login_manager.login_message_category = "info"

    with app.app_context():
        # --- 3. استيراد النماذج (Models) لضمان سلامة القاعدة ---
        # 🛡️ تصحيح سيادي: تم استيراد User فقط لأننا فصلنا البقية لتجنب ImportError
        from core.models.user import User
        # محاولة استيراد Order لتأمين الإحصائيات في الداشبورد
        try:
            from core.models.business import Order
        except ImportError:
            Order = None
        
        # إنشاء الجداول المفقودة وتحديث الهيكل تلقائياً
        try:
            db.create_all() 
            print("✅ تم فحص وتحديث هيكل الترسانة الرقمية لـ محجوب أونلاين بنجاح.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ تنبيه حوكمة البيانات: تعذر تحديث الهيكل تلقائياً: {e}")

        # --- 4. المعالجات السياقية (بيانات الهوية السيادية) ---
        @app.context_processor
        def utility_processor():
            def get_sovereign_data():
                """توليد المعرف السيادي بشكل آمن واحتياطي"""
                base_prefix = "MAH-963"
                # نستخدم رقم عشوائي حالياً لأن جدول الموردين (Vendor) غير موجود في هذا الملف
                rand_id = random.randint(1000, 9999)
                return {
                    "id": f"{base_prefix}{rand_id}", 
                    "wallet": f"W-{base_prefix}{rand_id}"
                }

            sov_data = get_sovereign_data()
            return dict(
                next_id=sov_data['id'],
                next_wallet=sov_data['wallet']
            )

        # --- 5. تسجيل مركز القيادة (Blueprints) ---
        from admin_panel import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

# --- 6. إدارة جلسات المستخدمين (خارج دالة create_app) ---
@login_manager.user_loader
def load_user(user_id):
    """تحميل المستخدم السيادي مع حماية الجلسة من الانهيار"""
    from core.models.user import User
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        db.session.rollback()
        return None
