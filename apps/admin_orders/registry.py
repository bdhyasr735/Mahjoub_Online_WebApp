# coding: utf-8
# 📂 apps/admin_orders/registry.py

from apps.admin_orders.routes import admin_orders_bp

# إعدادات القائمة الجانبية (تظهر تلقائياً في الإدارة)
MODULE_NAME = 'إدارة الطلبات'
MODULE_ICON = 'fas fa-boxes'
SHOW_IN_SUPPLIER = False  # يظهر للإدارة فقط

# الروابط التي ستظهر في الشريط الجانبي تحت هذا القسم مطابقة للأندبوينت الفعلي
LINKS = {
    'admin_orders.list_admin_orders': 'عرض الطلبات',
}

# الدالة التي يتم استدعاؤها تلقائياً بواسطة apps/__init__.py
def register_module(app):
    app.register_blueprint(admin_orders_bp)
    print("✅ [Module]: تم تفعيل موديول إدارة الطلبات بنجاح.")
