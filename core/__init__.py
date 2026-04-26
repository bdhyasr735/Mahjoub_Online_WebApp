from flask import Flask, session
from flask_login import LoginManager
from config import Config
import os

# --- 1. استيراد المحركات المركزية ---
from core.models import db

login_manager = LoginManager()

def create_app():
    # إنشاء نسخة التطبيق وتحديد مسارات الموارد المركزية
    app = Flask(__name__, 
                static_folder='../static', 
                template_folder='../templates')
    
    app.config.from_object(Config)
    
    # --- 2. ربط المحركات بنواة التطبيق ---
    db.init_app(app)
    login_manager.init_app(app)
    
    # --- 3. بروتوكولات الحماية ---
    login_manager.login_view = 'admin_panel.login'  
    login_manager.login_message = "يرجى إثبات هويتك للوصول إلى هذه المنطقة السيادية."
    login_manager.login_message_category = "info"

    with app.app_context():
        # استيراد الموديلات داخل السياق لضمان تسجيلها في قاعدة البيانات
        from core.models import User, Supplier, Product

        # --- 🔐 نظام الفصل الذكي بين الهويات (Multi-Auth) ---
        @login_manager.user_loader
        def load_user(user_id):
            try:
                # نعتمد على user_type المخزن في الجلسة لتوجيه الاستعلام للجدول الصحيح
                user_type = session.get('user_type')
                if user_type == 'supplier':
                    return Supplier.query.get(int(user_id))
                return User.query.get(int(user_id))
            except Exception:
                return None

        # --- 🔗 تسجيل بوابات النظام (Blueprints) ---
        try:
            # تسجيل بوابة الإدارة
            from admin_panel.routes import admin_bp
            app.register_blueprint(admin_bp, url_prefix='/admin')
            
            # تسجيل بوابة الموردين (استيراد supplier_bp من الملف الذي أنشأناه)
            # التأكد من استيرادها من المجلد الذي يحتوي على __init__.py الجديد
            from supplier_panel import supplier_bp
            app.register_blueprint(supplier_bp, url_prefix='/supplier')
            
            print("✅ [System] تم ربط جميع البوابات السيادية بنجاح.")
        except Exception as e:
            print(f"❌ [Critical Error] فشل في ربط البوابات السيادية: {e}")

        # --- 📊 معالج البيانات الشامل ---
        @app.context_processor
        def inject_global_data():
            try:
                # جلب عدد الطلبات المعلقة للموردين لعرضها في شريط التنبيهات للأدمن
                p_suppliers = Supplier.query.filter_by(is_approved=False).count()
                return dict(pending_suppliers_count=p_suppliers)
            except Exception:
                return dict(pending_suppliers_count=0)

    return app
