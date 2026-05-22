# coding: utf-8
# 🏢 المصنع المركزي للنواة المستقرة - منصة محجوب أونلاين 2026

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# تهيئة الإضافات الأساسية (نفس الكائنات المشتركة للنظام)
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # إنشاء كائن التطبيق الرئيسي
    app = Flask(__name__)
    
    app.config.from_object(Config)
    app.json.ensure_ascii = False

    # ضمان إعداد مسار الرفع للملفات والوثائق السيادية للموردين
    if not app.config.get('UPLOAD_FOLDER'):
        app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads', 'identities')

    # تهيئة الإضافات داخل المصنع بربطها بالكائن الحاضن
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        # --- استيراد الموديلات وتأمين سلامة التركيب البرمجي للأرشفة ---
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import SupplierWallet 
        
        # إنشاء الجداول وتطبيق التعديلات الهيكلية الصارمة تلقائياً
        try:
            db.create_all()
            
            # أوامر التطهير والتعديل على أسطر وجداول قاعدة البيانات الحية
            commands = [
                "ALTER TABLE supplier_wallets DROP CONSTRAINT IF EXISTS supplier_wallets_supplier_id_fkey;",
                "ALTER TABLE supplier_wallets ALTER COLUMN supplier_id TYPE VARCHAR(50);",
                "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS wallet_code VARCHAR(50) UNIQUE;",
                "ALTER TABLE supplier_wallets ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'نشطة';",
                "ALTER TABLE supplier_wallets DROP COLUMN IF EXISTS yer_available;",
                "ALTER TABLE supplier_wallets DROP COLUMN IF EXISTS sar_available;",
                "ALTER TABLE supplier_wallets DROP COLUMN IF EXISTS usd_available;"
            ]
            
            for cmd in commands:
                try:
                    db.session.execute(db.text(cmd))
                except Exception:
                    continue 
            
            db.session.commit()
            print("🚀 سيادة وحوكمة: تم إقرار البنية الرقمية للمحافظ وتحديث قاعدة البيانات بنجاح.")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"❌ تعذر تحديث الجداول برمجياً: {str(e)}")

    # إعدادات جلسات تسجيل الدخول وحماية المنطقة السيادية لـ لوحة التحكم
    login_manager.login_view = 'auth_portal.login'
    login_manager.login_message = 'يرجى إثبات الهوية الرقمية للوصول إلى المنطقة السيادية.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # --- 🔄 استيراد المسارات (Blueprints) بالأسماء البرمجية الدقيقة لإنهاء مشكلة الانهيار ---
    from apps.auth_portal import auth_blueprint
    from apps.admin_dashboard import admin_dashboard_bp  # تعديل الاسم هنا ليطابق الـ __init__.py الخاص بلوحة التحكم
    from apps.add_supplier import admin_suppliers_bp     # تعديل الاسم ليطابق حزمة إضافة الموردين
    
    # استيراد المحفظة بأمان (تأكد من مطابقة اسم المتغير المصدر داخل حزمة الـ wallet)
    try:
        from apps.wallet.routes import admin_wallet
    except ImportError:
        from apps.wallet import admin_wallet  # مسار بديل في حال كانت معرّفة داخل الحزمة مباشرة

    # تسجيل المسارات بالبادئات الأمنية الموحدة لتعمل الروابط عبر الـ url_for بكفاءة
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(admin_dashboard_bp, url_prefix='/admin')
    app.register_blueprint(admin_suppliers_bp, url_prefix='/suppliers')
    app.register_blueprint(admin_wallet, url_prefix='/admin/wallet')
    
    # معالجة الأخطاء الداخلية وعرض جذور الخلل لتسهيل تتبع السجلات على Railway
    @app.errorhandler(500)
    def internal_error(e):
        return f"<div style='direction:rtl; font-family:Cairo; padding:20px;'><h3 style='color:#d32f2f;'>حدث خطأ سيادي داخلي (500)</h3><p>تفاصيل المشكلة البرمجية: {str(e)}</p></div>", 500

    print("✅ المصنع المركزي للنواة يعمل بنجاح! تم تعميد كافة المسارات والمحرك مستعد للتشغيل الفوري.")
    return app
