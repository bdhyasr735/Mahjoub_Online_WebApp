# 📂 apps/orders/registry.py
from apps.orders.routes import orders_bp

MODULE_NAME = "الطلبات"
MODULE_ICON = "fa-shopping-cart"

# التصحيح: يجب أن يتطابق الـ endpoint تماماً مع اسم البلوبرينت المسجل في routes.py
# وبما أنك سجلت البلوبرينت باسم 'orders' في routes.py، يجب أن يكون الـ endpoint هو 'orders.dashboard'
LINKS = {
    "قائمة الطلبات": "orders.dashboard"
}

def register_module(app):
    try:
        # تأكد أن الـ url_prefix متوافق مع ما يتوقعه التطبيق
        app.register_blueprint(orders_bp, url_prefix='/orders')
        print("✅ [Registry]: تم تسجيل موديول 'Orders' بنجاح تحت المسار /orders.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'Orders': {e}")
