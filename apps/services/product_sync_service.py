from apps.services.product_sync_service import product_sync

# 1️⃣ إنشاء منتج وربطه بمورد
result = product_sync.create_product(
    title="منتج جديد",
    description="وصف المنتج",
    price=99.99,
    supplier_id=1  # 🔗 الربط التلقائي
)
print(result)

# 2️⃣ مزامنة منتج مع مورد
result = product_sync.sync_product_with_supplier(
    supplier_id=1,
    product_data={
        'title': 'منتج من المورد',
        'price': 149.99,
        'status': 'ACTIVE'
    }
)
print(result)

# 3️⃣ جلب منتجات مورد معين
products = product_sync.get_products_by_supplier(supplier_id=1)
for item in products:
    print(f"{item['product']['title']} - QID: {item['product']['qid']}")

# 4️⃣ حذف منتج مع حذف الربط
product_sync.delete_product(qid="qmr_123456", delete_mapping=True)
