# coding: utf-8
# 🏢 المصنع المركزي للنواة - منصة محجوب أونلاين 2026

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# إنشاء الكائنات المركزية كنسخ مستقلة لمنع التعارض الدائري
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # تعيين مجلد القوالب العام كخلفية احتياطية للتطبيق كاملاً
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)

    # 🛡️ التحديث السيادي لعام 2026: حل مشكلة تشفير النصوص العربية (Unicode) في Flask 3+
    # نقوم بحقن ترميز الـ UTF-8 مباشرة في محرك الـ JSON الخاص بـ Flask لضمان طباعة النصوص العربية بنقاء كامل
    app.json.ensure_ascii = False

    # تهيئة الإضافات بربطها بالتطبيق الحالي أولاً
    db.init_app(app)
    login_manager.init_app(app)

    # 🛡️ استدعاء النماذج الحوكمة فوراً بعد التهيئة لإجبار Flask و SQLAlchemy 
    # على تسجيل الجداول وأحداث توليد المعرفات والمحافظ تلقائياً في سياق النواة
    with app.app_context():
        # 🎯 تعديل حاسم لكسر الـ Circular Import: استيراد ملفات الموديلات فراداً وبشكل دقيق ومباشر
        import apps.models.admin_db
        import apps.models.supplier_db
        import apps.models.wallet_db
        print("🛡️ تم تعميد النماذج وإخضاع ملفات قواعد البيانات لسياق الـ SQLAlchemy بنجاح.")
        
        # 🔥 الإجراء الحوكمي الحاسم: إجبار المحرك على بناء الجداول فوراً وحقن الأعمدة سحابياً إن نقصت
        try:
            db.create_all()
            
            # 🎯 محرك التصحيح التلقائي السيادي للهيكل المالي وتوافق المعرف النصي (SUP-MAH9631)
            # 1. كسر القيد القديم مؤقتاً لشرط المفتاح الأجنبي
            db.session.execute(db.text("ALTER TABLE supplier_wallets DROP CONSTRAINT IF EXISTS supplier_wallets_supplier_id_fkey;"))
            
            # 2. تحويل العمود الإجباري إلى نوع نصي VARCHAR ليتطابق مع الـ sovereign_id المفرز
            db.session.execute(db.text("ALTER TABLE supplier_wallets ALTER COLUMN supplier_id TYPE VARCHAR(50);"))
            
            # 3. التأكد من حقن الأعمدة التأمينية للهيكل الأساسي إن لم تكن متواجدة
            db.session.execute(db.text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS wallet_code VARCHAR(50) UNIQUE;"))
            db.session.execute(db.text("ALTER TABLE supplier_wallets ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'نشطة';"))
            
            # 🛡️ التطهير الاستثنائي الحاسم: إسقاط الحقول الثابتة القديمة من قاعدة البيانات السحابية 
            # لتعمل الخصائص الحسابية الديناميكية (@property) المنفذة في البايثون بحرية كاملة وينتهي خطأ الـ NotNullViolation
            db.session.execute(db.text("ALTER TABLE supplier_wallets DROP COLUMN IF EXISTS yer_available;"))
            db.session.execute(db.text("ALTER TABLE supplier_wallets DROP COLUMN IF EXISTS sar_available;"))
            db.session.execute(db.text("ALTER TABLE supplier_wallets DROP COLUMN IF EXISTS usd_available;"))
            
            # 4. إعادة بناء المفتاح الأجنبي لربط المحفظة بالمورد بشكل سيادي مستقر ومتوافق نصياً
            db.session.execute(db.text("""
                ALTER TABLE supplier_wallets 
                ADD CONSTRAINT supplier_wallets_supplier_id_fkey 
                FOREIGN KEY (supplier_id) REFERENCES suppliers(sovereign_id);
            """))
            
            db.session.commit()
            print("🚀 سيادة وحوكمة: تم تطهير حقول الموازين الثابتة وإقرار البنية الرقمية النصية للمحافظ بنجاح تنفيذي مطلق.")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"❌ تعذر توليد أو تحديث الجداول برمجياً أثناء الإقلاع: {str(e)}")
        finally:
            db.session.close() # 🔓 تحرير فوري للاتصال لمنع الـ Locks والـ Deadlock عند الإقلاع

    # 🛡️ الحماية السيادية: تحديد المسار الكامل لـ Flask-Login
    login_manager.login_view = 'auth_portal.login'
    login_manager.login_message = 'يرجى إثبات الهوية الرقمية للوصول إلى المنطقة السيادية.'
    login_manager.login_message_category = 'warning'

    # 🔑 تعريف الـ user_loader لجلب الهوية من قاعدة البيانات
    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # 📥 استيراد البلوبرينتس الفرعية بشكل آمن ومباشر لمنع التداخل الدائري
    from apps.auth_portal import auth_blueprint
    from apps.admin_dashboard import admin_dashboard_blueprint
    
    # 🎯 التعديل الحاسم الأول: استيراد البلوبرينت الصحيح بالاسم المعرّف داخل الـ routes
    from apps.add_supplier.routes import admin_suppliers_bp

    # 💳 الاستيراد الحاسم والسيادي لمحرك المحافظ من مسار الحزمة التابع لـ routes
    from apps.wallet.routes import admin_wallet

    # ⚙️ تسجيل وعزل المسارات برمجياً لضمان استقرار المنصة بالكامل
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(admin_dashboard_blueprint, url_prefix='/admin')
    
    # 📦 التعديل الحاسم الثاني: تسجيل البلوبرينت بدون url_prefix لمنع تداخل المسارات وحل مشكلة الـ 404 والـ BuildError
    app.register_blueprint(admin_suppliers_bp)

    # 💰 تعميد وتسجيل محرك المحافظ والعمليات المادية الثلاثية بشكل رسمي في النواة
    app.register_blueprint(admin_wallet)

    return app
