# run.py
import os
import logging
from sqlalchemy import text
from core import create_app, db
from core.models.user import User
from core.models.supplier import Supplier
# استيراد البلوبرنت الخاص بلوحة التحكم لربطه بالمحرك الرئيسي
from admin_panel.routes import admin_bp 

# إعداد السجلات السيادية لمركز العمليات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Mahjoub_System")

# 1. تهيئة التطبيق المركزي
app = create_app()

# 2. تسجيل لوحة التحكم (Blueprint) مع بادئة المسار السيادية
# هذا السطر هو المفتاح لحل مشكلة 404
if not app.blueprints.get('admin'):
    app.register_blueprint(admin_bp, url_prefix='/admin')
    logger.info("📡 تم تفعيل مسارات لوحة التحكم تحت /admin")

def patch_database():
    """تحديث هيكل الجداول ليتوافق مع التعديلات السيادية الجديدة"""
    with app.app_context():
        sql_commands = [
            # --- تحديث جدول المستخدمين (Users) ---
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(150) UNIQUE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS supplier_id INTEGER REFERENCES suppliers(id);",
            
            # --- تحديث جدول الموردين (Suppliers) ---
            "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS identity_type VARCHAR(50);",
            "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS identity_image_url VARCHAR(255);",
            "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS sovereign_id VARCHAR(100);",
            "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS tier VARCHAR(50) DEFAULT 'مورد مبتدئ';",
            "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS balance_yer NUMERIC(20, 2) DEFAULT 0.00;",
            "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS balance_sar NUMERIC(20, 2) DEFAULT 0.00;",
            "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS balance_usd NUMERIC(20, 2) DEFAULT 0.00;"
        ]
        
        logger.info("🔍 جاري فحص وتحديث الترسانة الرقمية...")
        for cmd in sql_commands:
            try:
                db.session.execute(text(cmd))
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.debug(f"ℹ️ حقل موجود مسبقاً أو خطأ بسيط: {str(e)}")
        logger.info("✅ تم تحديث هيكل الجداول بنجاح.")

def initialize_system():
    """تهيئة النظام السيادي عند الإقلاع"""
    with app.app_context():
        try:
            # 1. إنشاء الجداول الأساسية التي لم تُبنى بعد
            db.create_all()
            
            # 2. إصلاح الأعمدة المفقودة (الجسر البرمجي)
            patch_database()
            
            # 3. تأمين حساب القائد علي محجوب (Admin)
            admin_username = "علي محجوب"
            admin = User.query.filter_by(username=admin_username).first()
            if not admin:
                new_admin = User(username=admin_username, role='admin', is_active_account=True)
                new_admin.set_password('123') 
                db.session.add(new_admin)
                db.session.commit()
                logger.info(f"👤 تم إنشاء حساب القائد: {admin_username}") 
            else:
                logger.info(f"✅ القائد {admin_username} في مركز القيادة.")
                
        except Exception as e:
            logger.error(f"⚠️ خطأ فادح أثناء التهيئة: {str(e)}")

# بروتوكول التشغيل (يمنع التكرار في وضع الـ Debug)
if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
    initialize_system()

if __name__ == "__main__":
    # تحديد المنفذ الخاص بـ Railway أو المنفذ الافتراضي 5000
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 انطلاق منصة محجوب أونلاين على المنفذ: {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
