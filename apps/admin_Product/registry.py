# coding: utf-8
# 📂 apps/admin_Product/registry.py

from flask import Blueprint
import logging

# 1. تعريف الـ Blueprint
admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')
logger = logging.getLogger(__name__)

# --- إعدادات التسجيل والظهور في القائمة الجانبية ---
MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box-open"
SHOW_IN_SUPPLIER = False 

LINKS = {
    "admin_product_bp.manage_products": "قائمة المنتجات",
    "admin_product_bp.add_product": "إضافة منتج"
}

# --- 🎨 ثيم الألوان الموحد للموديول ---
MODULE_THEME = {
    "deep_purple": "#2d144d",
    "royal_accent": "#4b0082",
    "gold_accent": "#d4af37",
    "royal_bg": "#f8f7fc"
}

# --- 💡 دالة التمرير التلقائي للألوان والإعدادات للقوالب ---
@admin_product_bp.context_processor
def inject_module_defaults():
    return dict(
        module_name=MODULE_NAME,
        module_icon=MODULE_ICON,
        show_in_supplier=SHOW_IN_SUPPLIER,
        module_links=LINKS,
        theme=MODULE_THEME
    )

def register_module(app):
    """دالة تسجيل الـ Blueprint وتعيين المسار الموحد للمنتجات"""
    try:
        app.register_blueprint(admin_product_bp, url_prefix='/admin/products')
        print("✅ [Registry]: تم تسجيل موديول 'إدارة المنتجات' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'إدارة المنتجات': {e}")

# 2. الاستيراد في النهاية لضمان ربط المسارات
from . import routes
