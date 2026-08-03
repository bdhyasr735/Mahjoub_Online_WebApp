# coding: utf-8
# 📂 apps/suppliers_orders/registry.py

MODULE_NAME = "طلبات الزبائن"
MODULE_ICON = "fas fa-shopping-cart"
SHOW_IN_SUPPLIER = True

# ✅ تم تصحيح الـ Endpoint ليتطابق مع ما هو موجود في orders.py
LINKS = {
    'suppliers_orders_bp.list_supplier_orders': '📦 إدارة الطلبات'
}

def register_module(app):
    from apps.suppliers_orders.routes import suppliers_orders_bp
    # ✅ حماية إضافية: التحقق من عدم التسجيل المسبق لتجنب أي أخطاء في الـ Blueprint
    if 'suppliers_orders_bp' not in app.blueprints:
        app.register_blueprint(suppliers_orders_bp, url_prefix='/supplier/orders')
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_orders' بنجاح.")
    else:
        print("ℹ️ [Registry]: موديول 'suppliers_orders' مسجل مسبقاً.")
