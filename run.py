import os
from apps import create_app
from apps.extensions import db
from sqlalchemy import text

app = create_app()

def run_db_migrations():
    """تحديث هيكل قاعدة البيانات تلقائياً عند الإقلاع"""
    with app.app_context():
        try:
            print("🔧 جاري التحقق من تحديثات قاعدة البيانات...")
            
            # أوامر SQL لإضافة الأعمدة إذا لم تكن موجودة
            commands = [
                "ALTER TABLE supplier_wallets ADD COLUMN IF NOT EXISTS _yer_total VARCHAR(255) DEFAULT '0.00'",
                "ALTER TABLE supplier_wallets ADD COLUMN IF NOT EXISTS _sar_total VARCHAR(255) DEFAULT '0.00'",
                "ALTER TABLE supplier_wallets ADD COLUMN IF NOT EXISTS _usd_total VARCHAR(255) DEFAULT '0.00'"
            ]
            
            for cmd in commands:
                db.session.execute(text(cmd))
            
            db.session.commit()
            print("✅ تم تحديث هيكل قاعدة البيانات بنجاح.")
        except Exception as e:
            print(f"⚠️ خطأ أثناء تحديث القاعدة: {e}")
            db.session.rollback()

# تشغيل الفحص قبل بدء السيرفر
run_db_migrations()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
