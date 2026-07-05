# 📂 apps/orders/registry.py

MODULE_NAME = "الطلبات"
MODULE_ICON = "fa-shopping-cart"

LINKS = {
    "قائمة الطلبات": "orders.dashboard"
}

def register_module(app):
    """دالة تسجيل موديول الطلبات"""
    try:
        # استيراد محلي لتجنب تعارض الاستيرادات
        from apps.orders.routes import orders_bp
        app.register_blueprint(orders_bp, url_prefix='/orders')
        print("✅ [Registry]: تم تسجيل موديول 'Orders' بنجاح.")
    except ImportError as e:
        print(f"❌ [Registry Error]: لا يمكن العثور على 'routes.py' في موديول 'orders': {e}")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'Orders': {e}")
