# core/__init__.py
from flask import Flask
from flask_wtf.csrf import CSRFProtect  # 🛡️ درع الحماية السيادي
from .extensions import db, login_manager 
from .setup import auth_loaders 

# تهيئة درع الحماية عالمياً
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, 
                static_folder='../static', 
                template_folder='../templates')
    
    # تحميل الإعدادات المركزية
    app.config.from_object('config.Config')
    
    # --- تفعيل الترسانة الرقمية والخدمات المركزية ---
    db.init_app(app)
    login_manager.init_app(app)
    
    # 🔓 يبقى معطلاً مؤقتاً لتجنب خطأ JSON.parse وحرف < الناتج عن رفض الطلبات
    # csrf.init_app(app) 
    
    login_manager.login_view = 'admin.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى الترسانة السيادية"

    with app.app_context():
        # 1. استيراد الموديلات لضمان وعي المحرك بها قبل التحديث
        from .models import User, Supplier, SupplierStaff
        
        # 2. بروتوكول التحديث التلقائي للهيكل (Auto-Migration)
        try:
            db.create_all()
            
            db_updates = [
                ("suppliers", "email", "VARCHAR(150)"),
                ("suppliers", "identity_image", "VARCHAR(255)"),
                ("suppliers", "identity_type", "VARCHAR(50)"),
                ("suppliers", "activity_type", "VARCHAR(100)"),
                ("suppliers", "bank_name", "VARCHAR(100)"),
                ("suppliers", "bank_acc", "VARCHAR(100)"),
                ("suppliers", "district", "VARCHAR(100)"),
                ("suppliers", "address_detail", "TEXT"),
                ("suppliers", "balance_yer", "NUMERIC(20, 2) DEFAULT 0.0"), 
                ("suppliers", "balance_sar", "NUMERIC(20, 2) DEFAULT 0.0"), 
                ("suppliers", "balance_usd", "NUMERIC(20, 2) DEFAULT 0.0"), 
                ("suppliers", "sovereign_id", "VARCHAR(100) UNIQUE"),       
                ("suppliers", "tier", "VARCHAR(50) DEFAULT 'مبتدئ'"),
                ("suppliers", "status", "VARCHAR(50) DEFAULT 'نشط'"),
                ("users", "full_name", "VARCHAR(150)"),
                ("users", "permissions", "TEXT DEFAULT '{}'"),
                ("users", "role", "VARCHAR(50) DEFAULT 'admin'"),
                ("users", "last_ip", "VARCHAR(45)")
            ]
            
            for table, col_name, col_type in db_updates:
                try:
                    db.session.execute(db.text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                except Exception:
                    pass 

            db.session.commit()
            print("✅ تم استكمال تحديث الهيكل السيادي بنجاح.")
            
        except Exception as e:
            print(f"⚠️ عطل تقني في تهيئة الجداول: {e}")
            db.session.rollback()

        # 3. تسجيل البلوبرنتات (Blueprint Registry)
        # تم تنظيف هذا القسم تماماً: الاستيراد يتم من الباقة مباشرة
        # والروابط يتم تسجيلها تلقائياً عبر __init__.py الخاص بـ admin_panel
        from admin_panel import admin_bp
        app.register_blueprint(admin_bp) 

    return app
