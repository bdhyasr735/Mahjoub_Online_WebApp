# run.py - تحديث دالة الإصلاح لتشمل الجدولين
def auto_fix_database():
    with app.app_context():
        try:
            print("🔧 جاري فحص هيكل قاعدة البيانات...")
            inspector = inspect(db.engine)
            
            # إصلاح جدول المحافظ
            if 'supplier_wallets' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('supplier_wallets')]
                for col in ['_yer_total', '_sar_total', '_usd_total']:
                    if col not in cols:
                        db.session.execute(text(f"ALTER TABLE supplier_wallets ADD COLUMN {col} VARCHAR(255) DEFAULT '0.00'"))
            
            # إصلاح جدول المعاملات
            if 'wallet_transactions' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('wallet_transactions')]
                for col in ['_amount', '_profit_margin', '_notes']:
                    if col not in cols:
                        db.session.execute(text(f"ALTER TABLE wallet_transactions ADD COLUMN {col} VARCHAR(255)"))
            
            db.session.commit()
            print("✅ تم تحديث هيكل الجداول بنجاح.")
        except Exception as e:
            print(f"❌ خطأ أثناء الإصلاح: {e}")
