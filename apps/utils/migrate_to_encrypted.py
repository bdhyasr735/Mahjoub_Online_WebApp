# coding: utf-8
from apps import create_app
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.statement_db import SupplierStatement
from apps.models.wallet_db import SupplierWallet, WalletTransaction

def run_migration():
    # 1. تهيئة بيئة التطبيق (App Factory)
    app = create_app()
    
    with app.app_context():
        print("🚀 بدء عملية الترحيل المشفر...")
        
        # 2. معالجة الموردين
        for s in Supplier.query.all():
            s.owner_name = s.owner_name 
            s.trade_name = s.trade_name
            print(f"✅ تم معالجة المورد: {s.sovereign_id}")
        
        # 3. معالجة الكشوفات
        for stmt in SupplierStatement.query.all():
            stmt.description = stmt.description
            stmt.debit = stmt.debit
            stmt.credit = stmt.credit
            stmt.running_balance = stmt.running_balance
            
        # 4. معالجة المحافظ
        for w in SupplierWallet.query.all():
            w.yer_total = w.yer_total
            w.sar_total = w.sar_total
            w.usd_total = w.usd_total
            
        # 5. معالجة الحركات
        for tx in WalletTransaction.query.all():
            tx.amount = tx.amount
            tx.profit_margin = tx.profit_margin
            tx.notes = tx.notes

        # 6. الحفظ النهائي في قاعدة البيانات
        db.session.commit()
        print("🎉 اكتملت عملية الترحيل بنجاح وتم تشفير كافة البيانات!")

if __name__ == "__main__":
    run_migration()
