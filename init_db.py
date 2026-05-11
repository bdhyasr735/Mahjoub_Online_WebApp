import os
import sys
from sqlalchemy import text
from werkzeug.security import generate_password_hash

# --- 1. بروتوكول تثبيت المسار (Railway Infrastructure) ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core import create_app, db
    from core.models.user import User
    from core.models.supplier import Supplier, SupplierStaff
    try:
        from core.models.business import Order
        from core.models.product import Product
    except ImportError:
        Order = None
        Product = None
except ImportError as e:
    print(f"❌ تعذر العثور على النواة (Core Models): {e}")
    sys.exit(1)

app = create_app()

def initialize_database():
    """
    بروتوكول تهيئة الترسانة الرقمية المستقرة - منصة محجوب أونلاين v3.6
    تم إيقاف 'بروتوكول التصفير' لضمان بقاء بيانات القائد للأبد.
    """
    with app.app_context():
        try:
            print("\n" + "="*60)
            print("🚀 بدء بروتوكول التحديث والتعميد - محجوب أونلاين")
            print("="*60)
            
            # [تم إيقاف الحذف] 1. تجاوز بروتوكول التصفير (Safe Harbor Protocol)
            # تم تعطيل DROP TABLE لضمان عدم ضياع بيانات الموردين المسجلين
            print("🛡️ وضع الحماية نشط: لن يتم حذف أي بيانات موجودة.")

            # 2. بناء الهيكل الرقمي (Schema Creation)
            # ينشئ الجداول الجديدة فقط (مثل supplier_staff) ولا يلمس الجداول الموجودة
            db.create_all() 
            print("✅ تم فحص وبناء الهياكل الجديدة (Tables Verified).")
            
            # 3. ترميم الأعمدة وتحديث الخزينة (Sovereign Alterations)
            # نضمن وجود الحقول الجديدة التي أضفناها في ملفات models
            with db.engine.connect() as connection:
                alter_queries = [
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'admin';",
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS supplier_id INTEGER REFERENCES suppliers(id);",
                    "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS tier VARCHAR(50) DEFAULT 'مبتدئ';",
                    "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS mint_sovereign_id VARCHAR(100) UNIQUE;",
                    "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS balance_sar FLOAT DEFAULT 0.0;",
                    "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS balance_usd FLOAT DEFAULT 0.0;"
                ]
                for query in alter_queries:
                    try:
                        connection.execute(text(query))
                        connection.commit()
                    except Exception: 
                        pass 
            print("✅ تم تعميد الحقول السيادية الجديدة في قاعدة البيانات.")

            # 4. تأمين حساب المؤسس "علي محجوب"
            admin_user = User.query.filter_by(username="علي محجوب").first()
            if not admin_user:
                new_admin = User(
                    username="علي محجوب",
                    email='admin@mahjoub.online',
                    role='admin'
                )
                new_admin.set_password('123')
                db.session.add(new_admin)
                print("👤 تم إنشاء حساب المؤسس السيادي (علي محجوب) بنجاح.")
            else:
                admin_user.role = 'admin'
                print("ℹ️ حساب المؤسس موجود مسبقاً وتَم حفظ بياناته.")

            db.session.commit()
            print("\n🌟 المحرك يعمل الآن بنظام الاستقرار الكامل.")
            print("="*60 + "\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ تعثر البروتوكول بسبب: {str(e)}")

if __name__ == "__main__":
    initialize_database()
