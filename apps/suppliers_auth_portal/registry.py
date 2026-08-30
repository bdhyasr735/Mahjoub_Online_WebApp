# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/registry.py

from flask import Blueprint

def register_module(app):
    """تسجيل موديول بوابة المصادقة للموردين."""
    try:
        from apps.suppliers_auth_portal.routes import suppliers_bp
        if not suppliers_bp.name in app.blueprints:
            app.register_blueprint(suppliers_bp, url_prefix='/supplier')
        print("✅ [بوابة الموردين]: تم تسجيل الموديول بنجاح عبر نظام التسجيل الديناميكي.")
    except Exception as e:
        print(f"❌ [خطأ تسجيل موديول الموردين]: {e}")

# تعريف القائمة الجانبية وعناصر التنقل الخاصة بالموردين ضمن لوحة التحكم
NAV_ITEMS = [
    {"endpoint": "suppliers_bp.dashboard", "title": "لوحة تحكم المورد"},
    {"endpoint": "suppliers_bp.profile", "title": "إعدادات المتجر والحساب"},
    {"endpoint": "suppliers_bp.wallet", "title": "المحفظة والمعاملات المالیة"},
    {"endpoint": "suppliers_bp.products", "title": "إدارة المنتجات والطلبات"}
]

MODULE_NAME = "بوابة الموردين"
MODULE_ICON = "fa-store"
SHOW_IN_SUPPLIER = True
