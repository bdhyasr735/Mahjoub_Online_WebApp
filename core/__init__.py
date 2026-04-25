from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

# تهيئة الكائنات الأساسية خارج الدالة لضمان توفرها في كامل النظام
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # 1. إنشاء نسخة التطبيق وتحديد مسارات الملفات الثابتة والقوالب العامة
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    app.config.from_object(Config)
    
    # 2. ربط المكتبات بالتطبيق
    db.init_app(app)
    login_manager.init_app(app)
    
    # 3. إعدادات نظام الحماية وتسجيل الدخول
    login_manager.login_view = 'admin_panel.login'  
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى هذه المنطقة السيادية."
    login_manager.login_message_category = "info"

    with app.app_context():
        # --- 🛡️ استيراد الموديلات السيادية ---
        from core.models.user import User
        from core.models.supplier import Supplier
        from core.models.product import Product
        
        # --- 🔐 نظام التعرف الذكي والمطور على الهوية ---
        @login_manager.user_loader
        def load_user(user_id):
            try:
                # التعديل الجوهري: نبحث في الجدولين ونتأكد من هوية الكائن المسجل حالياً
                # نبدأ بالمورد أولاً لأن مشكلة "الفراغ" تظهر دائماً في بوابة الموردين
                supplier = Supplier.query.get(int(user_id))
                if supplier:
                    return supplier
                
                # إذا لم يكن مورداً، نبحث في جدول الأدمن (القائد)
                admin = User.query.get(int(user_id))
                if admin:
                    return admin
                
                return None
            except Exception as e:
                print(f"⚠️ [Auth Error] فشل تحميل الهوية: {e}")
                return None

        # --- 🔗 تسجيل بوابات النظام (Blueprints) ---
        try:
            # تسجيل لوحة الإدارة المركزية
            from admin_panel.routes import admin_bp
            app.register_blueprint(admin_bp, url_prefix='/admin')
            
            # تسجيل بوابة الموردين المحدثة
            from supplier_panel import supplier_bp
            app.register_blueprint(supplier_bp, url_prefix='/supplier')
            
            print("✅ [System] تم ربط جميع المسارات السيادية (الآدمن والموردين) بنجاح.")
        except Exception as e:
            print(f"❌ [Critical Error] فشل في تحميل بوابات النظام: {e}")

        # --- 📊 نظام العدادات التلقائي (Context Processor) ---
        @app.context_processor
        def inject_global_data():
            try:
                p_suppliers = Supplier.query.filter_by(is_approved=False).count()
                return dict(pending_suppliers_count=p_suppliers)
            except:
                return dict(pending_suppliers_count=0)

    return app
