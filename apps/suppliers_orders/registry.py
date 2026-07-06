# coding: utf-8
# 📂 apps/suppliers_orders/registry.py

from apps.suppliers_orders.routes import suppliers_orders_bp 

# 1. إعدادات الموديول
MODULE_NAME = "الطلبات"
MODULE_ICON = "fas fa-shopping-cart"
SHOW_IN_SUPPLIER = True

# 2. الروابط (تم التأكد من تطابق اسم الـ blueprint واسم الدالة)
LINKS = {
    "الطلبات": "suppliers_orders.index"
}

def register_module(app):
    """
    تسجيل موديول الطلبات في النظام
    """
    try:
        # تسجيل الـ Blueprint
        app.register_blueprint(suppliers_orders_bp, url_prefix='/supplier/orders')
        
        # رسالة تأكيد للـ Logs لضمان أن النظام يرى الروابط بشكل صحيح
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_orders' بنجاح.")
        print(f"🔗 الرابط المسجل هو: suppliers_orders.index")
        
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'suppliers_orders': {e}")
