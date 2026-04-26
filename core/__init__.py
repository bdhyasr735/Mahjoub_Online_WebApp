from flask import Flask, session
from flask_login import LoginManager
from config import Config
import os

# --- 1. استيراد المحركات المركزية ---
# نستورد db فقط هنا لضمان وجود محرك واحد لكل النظام
from core.models import db

login_manager = LoginManager()

def create_app():
    # إنشاء نسخة التطبيق وتحديد مسارات الموارد
    app = Flask(__name__, 
                static_folder='../static', 
                template_folder='../templates')
    
    # تحميل الإعدادات (Database URI, Secret Key, etc.)
    app.config.from_object(Config)
    
    # --- 2. ربط المحركات بنواة التطبيق ---
    db.init_app(app)
    login_manager.init_app(app)
    
    # --- 3. بروتوكولات الحماية وتسجيل الدخول ---
    # توجيه المستخدم لصفحة دخول الإدارة كخيار افتراضي
    login_manager.login_view = 'admin_panel.login'  
    login_manager.login_message = "يرجى إثبات هويتك للوصول إلى هذه المنطقة السيادية."
    login_manager.login_message_category = "info"

    with app.app_context():
        # استيراد الموديلات داخل السياق لضمان تسجيلها
        from core.models import User, Supplier, Product

        # --- 🔐 نظام الفصل الذكي بين الهويات (Multi-Auth) ---
        @login_manager.user_loader
        def load_user(user_id):
            try:
                # التحقق من نوع الجلسة لتحديد أي جدول نبحث فيه (أدمن أم مورد)
                user_type = session.get('user_type')
                if user_type == 'supplier':
                    return Supplier.query.get(int(user_id))
                return User.query.get(int(user_id))
            except Exception:
                return None

        # --- 🔗 تسجيل بوابات النظام (Blueprints) ---
        try:
            # 1. بوابة الإدارة المركزية
            from admin_panel.routes import admin_bp
            app.register_blueprint(admin_bp, url_prefix='/admin')
            
            # 2. بوابة الموردين (الحل النهائي لخطأ 404)
            from supplier_panel import supplier_bp
            app.register_blueprint(supplier_bp, url_prefix='/supplier')
            
            print("✅ [System] تم ربط البوابات السيادية (Admin & Supplier) بنجاح.")
        except Exception as e:
            print(f"❌ [Critical Error] فشل في ربط البوابات: {e}")

        # --- 📊 معالج البيانات الشامل (Context Processor) ---
        # يجعل الإحصائيات (مثل الموردين المعلقين) متاحة لجميع صفحات القوالب
        @app.context_processor
        def inject_global_data():
            try:
                p_suppliers = Supplier.query.filter_by(is_approved=False).count()
                return dict(pending_suppliers_count=p_suppliers)
            except Exception:
                return dict(pending_suppliers_count=0)

    return app
