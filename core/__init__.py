import re
import random
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# إنشاء كائنات النظام الأساسية (العمود الفقري للترسانة الرقمية)
db = SQLAlchemy()
login_manager = LoginManager()

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

    # --- 2. تهيئة الإضافات الأساسية ---
    db.init_app(app)
    login_manager.init_app(app)
    
    # حوكمة الدخول وتوجيه غير المصرح لهم إلى لوحة الإدارة
    login_manager.login_view = 'admin.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى النظام السيادي."
    login_manager.login_message_category = "info"

    with app.app_context():
        # --- 3. استيراد النماذج (Models) لضمان سلامة القاعدة ---
        from core.models.user import User
        from core.models.vendor import Vendor
        
        # 🛡️ تصحيح الترسانة: إنشاء الجداول المفقودة وتحديث الهيكل
        try:
            db.create_all() 
            print("✅ تم فحص وتحديث هيكل الترسانة الرقمية بنجاح.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ تنبيه حوكمة البيانات: تعذر تحديث الهيكل تلقائياً: {e}")
        
        # --- 4. إدارة جلسات المستخدمين (User Loader) ---
        @login_manager.user_loader
        def load_user(user_id):
            """تحميل المستخدم مع منع تعليق الاتصال بقاعدة البيانات"""
            try:
                return User.query.get(int(user_id))
            except Exception as e:
                db.session.rollback()
                print(f"❌ خطأ في محمل المستخدم: {e}")
                return None

        # --- 5. المعالجات السياقية (بيانات الهوية السيادية) ---
        @app.context_processor
        def utility_processor():
            def get_sovereign_data():
                """توليد المعرف MAH-963 والمحفظة برقم تسلسلي موحد"""
                base_prefix = "MAH-963"
                try:
                    # استعلام خفيف لضمان دقة التسلسل
                    count = db.session.query(Vendor.id).count() if Vendor else 0
                    next_num = count + 1
                    final_serial = f"{base_prefix}{next_num}"
                    
                    return {
                        "id": final_serial,
                        "wallet": f"W-{final_serial}"
                    }
                except Exception as e:
                    db.session.rollback()
                    # حل احتياطي ذكي لمنع توقف واجهات الإدخال
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

        # --- 6. تسجيل مركز القيادة (Blueprints) ---
        # ملاحظة: الاستيراد هنا يمنع مشاكل الاستيراد الدائري نهائياً
        from admin_panel import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
