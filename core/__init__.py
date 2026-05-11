# core/__init__.py
from flask import Flask
from flask_wtf.csrf import CSRFProtect  # 🛡️ استيراد درع الحماية السيادي
from .extensions import db, login_manager 
from .setup import auth_loaders 

# تهيئة درع الحماية عالمياً لمنع هجمات التزييف
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, 
                static_folder='../static', 
                template_folder='../templates')
    
    # تحميل الإعدادات المركزية (تأكد من وجود SECRET_KEY في config.Config)
    app.config.from_object('config.Config')
    
    # --- تفعيل الترسانة الرقمية والخدمات المركزية ---
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)  # ✅ تفعيل الحماية: هذا السطر ينهي خطأ 'csrf_token' is undefined
    
    login_manager.login_view = 'admin.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى الترسانة السيادية"

    with app.app_context():
        # 1. استيراد الموديلات المطهّرة لضمان وعي المحرك بها
        from .models import User, Supplier, SupplierStaff
        
        # 2. بروتوكول التحديث التلقائي للهيكل (Auto-Migration)
        try:
            db.create_all()
            
            # قائمة التحديثات السيادية للجداول لضمان توافق Railway مع الكود الجديد
            db_updates = [
                # جداول الموردين
                ("suppliers", "email", "VARCHAR(150)"),
                ("suppliers", "identity_image", "VARCHAR(255)"),
                ("suppliers", "balance_yer", "NUMERIC(20, 2) DEFAULT 0.0"), 
                ("suppliers", "balance_sar", "NUMERIC(20, 2) DEFAULT 0.0"), 
                ("suppliers", "balance_usd", "NUMERIC(20, 2) DEFAULT 0.0"), 
                ("suppliers", "sovereign_id", "VARCHAR(100) UNIQUE"),       
                ("suppliers", "tier", "VARCHAR(50) DEFAULT 'مبتدئ'"),
                # جداول المستخدمين (نظام الحوكمة الجديد)
                ("users", "full_name", "VARCHAR(150)"),
                ("users", "permissions", "TEXT DEFAULT '{}'"),
                ("users", "role", "VARCHAR(50) DEFAULT 'admin'"),
                ("users", "last_ip", "VARCHAR(45)")
            ]
            
            for table, col_name, col_type in db_updates:
                try:
                    db.session.execute(db.text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                except Exception:
                    pass # تخطي في حال كان الحقل موجوداً مسبقاً

            db.session.commit()
            
            # 3. بروتوكول تثبيت الهوية السيادية للقائد
            try:
                boss = Supplier.query.filter_by(trade_name="علي محجوب").first()
                if boss and not boss.sovereign_id:
                    boss.generate_sovereign_codes() 
                    db.session.commit()
                    print("✅ تم تعميد الهوية السيادية للقائد بنجاح.")
            except Exception as e:
                db.session.rollback()
                print(f"⚠️ تنبيه أثناء تعميد الهوية: {e}")

            print("✅ تم استكمال الترسانة وتطهير الهيكل بنجاح.")
            
        except Exception as e:
            print(f"⚠️ عطل سيادي في التهيئة: {e}")
            db.session.rollback()

        # 4. تسجيل البلوبرنتات لربط الواجهات بالمحرك
        from admin_panel import admin_bp
        # تسجيل نظام الطاقم والخدمات لضمان تفعيل الروابط السيادية
        from admin_panel import supplier_service_routes 
        from admin_panel import staff_routes
        
        app.register_blueprint(admin_bp) 

    return app
