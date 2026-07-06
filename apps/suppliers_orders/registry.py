# coding: utf-8
# 📂 apps/suppliers_orders/registry.py

# تأكد من استيراد الاسم الصحيح للـ Blueprint من ملف الـ routes الخاص بالطلبات
from apps.suppliers_orders.routes import suppliers_orders_bp 

MODULE_NAME = "الطلبات"
MODULE_ICON = "fas fa-shopping-cart"
SHOW_IN_SUPPLIER = True

LINKS = {
    "الطلبات": "suppliers_orders.index"
}

def register_module(app):
    try:
        app.register_blueprint(suppliers_orders_bp, url_prefix='/supplier/orders')
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_orders' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: {e}")
