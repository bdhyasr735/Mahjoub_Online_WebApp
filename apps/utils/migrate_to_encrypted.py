# coding: utf-8
from apps import create_app
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.statement_db import SupplierStatement
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.admin_db import AdminUser

def run_migration():
    app = create_app()
    with app.app_context():
        print("🚀 بدء عملية الترحيل المشفر...")
        
        # 1. ترحيل الموردين
        for s in Supplier.query.all():
            s.owner_name = s.owner_name 
            s.trade_name = s.trade_name
            print(f"✅ المورد: {s.sovereign_id}")
        
        # 2. ترحيل كشوفات الحسابات
        for stmt in SupplierStatement.query.all():
            stmt.description = stmt.description
            stmt.debit = stmt.debit
            stmt.credit = stmt.credit
            stmt.running_balance = stmt.running_balance
        
        # 3. ترحيل المحافظ
        for w in SupplierWallet.query.all():
            w.yer_total = w.yer_total
            w.sar_total = w.sar_total
            w.usd_total = w.usd_total
            
        # 4. ترحيل الحركات
        for tx in WalletTransaction.query.all():
            tx.amount = tx.amount
            tx.profit_margin = tx.profit_margin
            tx.notes = tx.notes

        db.session.commit()
        print("🎉 اكتملت عملية الترحيل لجميع البيانات بنجاح!")

if __name__ == "__main__":
    run_migration()
