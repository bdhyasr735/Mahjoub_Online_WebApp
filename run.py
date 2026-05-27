# coding: utf-8
import os
from apps import create_app
from apps.extensions import db
from sqlalchemy import text # مهم جداً

app = create_app()

# دالة الإصلاح التلقائي الذكية
def apply_schema_fixes():
    with app.app_context():
        try:
            print("🔧 جاري فحص وتحديث هيكل قاعدة البيانات...")
            
            # تحديث جدول الموردين (إضافة الأعمدة الجديدة فقط)
            db.session.execute(text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS category VARCHAR(50) DEFAULT 'عام'"))
            db.session.execute(text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS behavior_score FLOAT DEFAULT 100.0"))
            db.session.execute(text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS total_transactions INTEGER DEFAULT 0"))
            
            # تحديث جدول المحافظ (إضافة الأعمدة الجديدة فقط)
            db.session.execute(text("ALTER TABLE supplier_wallets ADD COLUMN IF NOT EXISTS _yer_total VARCHAR(255) DEFAULT '0.00'"))
            db.session.execute(text("ALTER TABLE supplier_wallets ADD COLUMN IF NOT EXISTS _sar_total VARCHAR(255) DEFAULT '0.00'"))
            db.session.execute(text("ALTER TABLE supplier_wallets ADD COLUMN IF NOT EXISTS _usd_total VARCHAR(255) DEFAULT '0.00'"))
            
            db.session.commit()
            print("✅ تم تحديث القاعدة بنجاح. لا تقلق، بياناتك القديمة سليمة.")
        except Exception as e:
            print(f"⚠️ خطأ أثناء تحديث القاعدة: {e}")
            db.session.rollback()

from sqlalchemy import text
from apps.extensions import db

# ضع هذا الكود داخل ملف التشغيل الرئيسي (run.py أو main.py)
# تأكد من استدعاء هذه الدالة بعد إعداد الـ app وقبل تشغيله
def fix_database_schema():
    with app.app_context():
        try:
            # إضافة الأعمدة الناقصة في جدول المحافظ
            db.session.execute(text("ALTER TABLE supplier_wallets ADD COLUMN IF NOT EXISTS _yer_total VARCHAR(255) DEFAULT '0.00'"))
            db.session.execute(text("ALTER TABLE supplier_wallets ADD COLUMN IF NOT EXISTS _sar_total VARCHAR(255) DEFAULT '0.00'"))
            db.session.execute(text("ALTER TABLE supplier_wallets ADD COLUMN IF NOT EXISTS _usd_total VARCHAR(255) DEFAULT '0.00'"))
            db.session.commit()
            print("✅ تم تحديث هيكل قاعدة البيانات وإضافة الأعمدة المشفرة بنجاح.")
        except Exception as e:
            print(f"❌ فشل تحديث القاعدة: {e}")

# قم باستدعاء الدالة هنا قبل app.run()
# fix_database_schema()


# تشغيل الفحص عند الإقلاع
apply_schema_fixes()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
