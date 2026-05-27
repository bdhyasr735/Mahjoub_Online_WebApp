# coding: utf-8
import os
from apps import create_app
from apps.extensions import db
from sqlalchemy import text, inspect

app = create_app()

def auto_fix_database():
    """دالة الإصلاح الذاتي لقاعدة البيانات"""
    with app.app_context():
        try:
            print("🔧 جاري فحص هيكل قاعدة البيانات...")
            inspector = inspect(db.engine)
            
            # إصلاح جدول المعاملات (Wallet Transactions)
            if 'wallet_transactions' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('wallet_transactions')]
                for col in ['_amount', '_profit_margin', '_notes']:
                    if col not in cols:
                        print(f"⚠️ إضافة العمود المفقود: {col}")
                        db.session.execute(text(f"ALTER TABLE wallet_transactions ADD COLUMN {col} VARCHAR(255)"))
                db.session.commit()
                
            # إصلاح جدول المحافظ (Supplier Wallets)
            if 'supplier_wallets' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('supplier_wallets')]
                for col in ['_yer_total', '_sar_total', '_usd_total']:
                    if col not in cols:
                        print(f"⚠️ إضافة العمود المفقود: {col}")
                        db.session.execute(text(f"ALTER TABLE supplier_wallets ADD COLUMN {col} VARCHAR(255)"))
                db.session.commit()
                
            print("🚀 قاعدة البيانات محدثة وجاهزة للعمل.")
        except Exception as e:
            print(f"❌ خطأ أثناء التحديث التلقائي: {str(e)}")
            db.session.rollback()

# تشغيل الفحص قبل بدء التطبيق
auto_fix_database()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
