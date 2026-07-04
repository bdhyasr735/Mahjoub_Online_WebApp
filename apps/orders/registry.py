# coding: utf-8
# 📂 apps/orders/registry.py

from apps.orders.routes import orders_bp

# إعدادات الموديول للظهور في القائمة الجانبية
MODULE_NAME = "الطلبات"
MODULE_ICON = "fa-shopping-cart"

# تعريف الروابط المتاحة لهذا الموديول
# تأكد من استبدال 'index' باسم الدالة الموجودة فعلياً في ملف routes.py الخاص بالطلبات
LINKS = {
    "قائمة الطلبات": "orders_bp.index"
}

def register_module(app):
    """
    دالة تسجيل موديول الطلبات في التطبيق الرئيسي
    تستخدم من قبل النظام لاكتشاف الموديول وتسجيل مساراته
    """
    try:
        app.register_blueprint(orders_bp, url_prefix='/orders')
        print("✅ [Registry]: تم تسجيل موديول 'Orders' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'Orders': {e}")
