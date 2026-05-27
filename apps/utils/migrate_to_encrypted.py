# coding: utf-8
# 🔐 سكربت ترحيل البيانات إلى النظام المشفر - منصة محجوب أونلاين 2026
from apps import db
from apps.models.supplier_db import Supplier
from apps.models.statement_db import SupplierStatement
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.admin_db import AdminUser

def run_migration():
    print("🚀 بدء عملية الترحيل المشفر...")
    
    # 1. ترحيل الموردين
    suppliers = Supplier.query.all()
    for s in suppliers:
        s.owner_name = s.owner_name  # التشفير يتم تلقائياً عبر @property
        s.trade_name = s.trade_name
        print(f"✅ تم تشفير بيانات المورد: {s.sovereign_id}")
    
    # 2. ترحيل كشوفات الحسابات
    statements = SupplierStatement.query.all()
    for stmt in statements:
        stmt.description = stmt.description
        stmt.debit = stmt.debit
        stmt.credit = stmt.credit
        stmt.running_balance = stmt.running_balance
    
    # 3. ترحيل المحافظ والحركات
    wallets = SupplierWallet.query.all()
    for w in wallets:
        w.yer_total = w.yer_total
        w.sar_total = w.sar_total
        w.usd_total = w.usd_total
        
    transactions = WalletTransaction.query.all()
    for tx in transactions:
        tx.amount = tx.amount
        tx.profit_margin = tx.profit_margin
        tx.notes = tx.notes

    # 4. ترحيل مديري النظام
    admins = AdminUser.query.all()
    for admin
