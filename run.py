# coding: utf-8
from apps import create_app
from apps.extensions import db
from sqlalchemy import text, inspect
import os

app = create_app()

def auto_fix_db():
    with app.app_context():
        try:
            print("🔧 جاري التحقق من هيكل قاعدة البيانات...")
            inspector = inspect(db.engine)
            
            # التأكد من وجود الجدول أولاً
            if 'wallet_transactions' in inspector.get_table_names():
                # الحصول على قائمة الأعمدة الحالية
                columns = [c['name'] for c in inspector.get_columns('wallet_transactions')]
                
                # الأعمدة التي يحتاجها الكود الجديد
                needed_cols = ['_amount', '_profit_margin', '_notes']
                
                for col in needed_cols:
                    if col not in columns:
                        print(f"➕ جاري إضافة العمود المفقود: {col}")
                        db.session.execute(text(f"ALTER TABLE wallet_transactions ADD COLUMN {col} VARCHAR(255)"))
                
                db.session.commit()
                print("✅ تم تحديث أعمدة قاعدة البيانات بنجاح.")
        except Exception as e:
            print(f"❌ خطأ أثناء الإصلاح التلقائي: {e}")
            db.session.rollback()

# استدعاء دالة الإصلاح قبل تشغيل التطبيق
auto_fix_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
