# -*- coding: utf-8 -*-
# 📂 apps/suppliers_dashboard/__init__.py

from apps.suppliers_dashboard.routes import suppliers_dashboard_bp

# خصائص وصفية وميتاداتا للموديول متوافقة مع محجوب أونلاين
MODULE_NAME = "لوحة تحكم الموردين"
DISPLAY_NAME = "لوحة تحكم الموردين"
MODULE_ICON = "fa-chart-pie"
SHOW_IN_SUPPLIER = True

# تعريف الروابط وروابط القوائم الجانبية (Navigation & Links)
NAV_ITEMS = [
    {
        'title': 'لوحة التحكم',
        'endpoint': 'suppliers_dashboard.index'
    }
]

LINKS = {
    'suppliers_dashboard.index': 'لوحة تحكم الموردين'
}

def register_module(app):
    """دالة تسجيل الموديول ديناميكياً في التطبيق الرئيسي"""
    if suppliers_dashboard_bp.name not in app.blueprints:
        app.register_blueprint(suppliers_dashboard_bp)
        print(f"✅ [Registry Supplier]: تم تسجيل موديول لوحة تحكم الموردين بنجاح.")

def init_app(app):
    """تهيئة إضافية للموديول إن وجدت"""
    pass
