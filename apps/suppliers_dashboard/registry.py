# -*- coding: utf-8 -*-
# 📂 apps/suppliers_dashboard/registry.py

from apps.suppliers_dashboard.routes import suppliers_dashboard_bp

# ============================================
# معلومات الموديول للتسجيل الديناميكي
# ============================================
MODULE_NAME = "suppliers_dashboard"
DISPLAY_NAME = "لوحة التحكم"
MODULE_ICON = "fa-chart-pie"
IS_LAYOUT_CONTAINER = True
SHOW_IN_SUPPLIER = True

# ============================================
# دالة تسجيل الموديول (مطلوبة للتسجيل الديناميكي)
# ============================================
def register_module(app):
    """تسجيل هيكل لوحة تحكم الموردين"""
    if suppliers_dashboard_bp.name not in app.blueprints:
        app.register_blueprint(suppliers_dashboard_bp)
        print(f"✅ [Registry Supplier Layout]: تم تسجيل هيكل لوحة تحكم الموردين بنجاح.")

def init_app(app):
    """تهيئة الموديول (اختياري)"""
    pass
