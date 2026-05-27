# coding: utf-8
from apps import create_app
from apps.extensions import db  # الاستيراد الصحيح من ملف الامتدادات
from apps.models.supplier_db import Supplier
from apps.models.statement_db import SupplierStatement
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.admin_db import AdminUser

def run_migration():
    # تهيئة المصنع أولاً ليعمل كل شيء
    app = create_app()
    with app.app_context():
        print("🚀 بدء عملية الترحيل المشفر...")
        
        # 1. ترحيل الموردين
        suppliers = Supplier.query.all()
        for s in suppliers:
            # التشفير يحدث هنا بفضل خصائص الموديل
            s.owner_name = s.owner_name 
            s.trade_name = s.trade_name
            print(f"✅ تم معالجة المورد: {s.sovereign_id}")
        
        # 2. ترحيل كشوفات الحسابات
        statements = SupplierStatement.query.all()
        for stmt in statements:
            stmt.description = stmt.description
            # بقية الحقول...
            
        # ... (أكمل باقي الترحيل بنفس الطريقة) ...

        db.session.commit()
        print("🎉 اكتملت العملية بنجاح!")

if __name__ == "__main__":
    run_migration()
