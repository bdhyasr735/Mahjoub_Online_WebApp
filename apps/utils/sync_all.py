# coding: utf-8
# 📂 apps/utils/sync_all.py - محرك المزامنة الذكي

from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
from apps.utils.orders_engine import get_pending_orders
from apps.extensions import db

def run_sync():
    print("🚀 بدء دورة المزامنة المالية...")
    
    # 1. جلب الطلبات المعلقة من قمرة
    orders = get_pending_orders()
    if not orders:
        print("✅ لا توجد طلبات جديدة للتسوية.")
        return

    for order in orders:
        order_id = order.get('id')
        total_price = float(order.get('totalPrice', 0))
        
        # 2. استخراج الـ Tags من الطلب لتحديد المورد
        # نفترض أن الـ tag للمورد موجود داخل الـ lineItems
        for item in order.get('lineItems', []):
            tags = item.get('product', {}).get('tags', [])
            
            for tag in tags:
                # 3. البحث عن المورد في قاعدة البيانات باستخدام الـ tag
                # هنا نبحث عن المورد الذي يملك هذا الـ tag في sovereign_id
                supplier = Supplier.query.filter_by(sovereign_id=tag).first()
                
                if supplier and supplier.wallet:
                    # 4. تسوية مالية: إضافة الرصيد للمحفظة
                    # نستخدم add_transaction الذي أنشأناه في wallet_db
                    supplier.wallet.add_transaction(
                        amount=total_price,
                        currency='SAR', # أو العملة المعتمدة
                        transaction_type='credit',
                        order_id=order_id,
                        description=f"تسوية مالية للطلب رقم {order_id}"
                    )
                    print(f"💰 تم تحديث محفظة المورد {supplier.username} للطلب {order_id}")

    db.session.commit()
    print("✅ تمت المزامنة بنجاح!")

if __name__ == "__main__":
    run_sync()
