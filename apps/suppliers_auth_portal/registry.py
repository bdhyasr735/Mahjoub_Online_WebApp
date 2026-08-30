# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/registry.py

# تم إزالة تسجيل البوابة من هنا لأنها مسجلة يدوياً في apps/__init__.py لتجنب التكرار.

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
