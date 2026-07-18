# coding: utf-8
# 📂 apps/admin_Product/registry.py

from flask import Blueprint
import logging

# 1. تعريف الـ Blueprint (يتم استخدامه في ملفات الـ routes الأخرى)
admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')
logger = logging.getLogger(__name__)

# --- إعدادات التسجيل والظهور في القائمة الجانبية ---
MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box-open"
SHOW_IN_SUPPLIER = False 

# ملاحظة: مفاتيح LINKS يجب أن تطابق أسماء الدوال في ملفات الـ routes
LINKS = {
    "admin_product_bp.manage_products": "قائمة المنتجات",
    "admin_product_bp.add_product": "إضافة منتج"
}

def register_module(app):
    """دالة تسجيل الـ Blueprint وتعيين المسار الموحد للمنتجات"""
    try:
        app.register_blueprint(admin_product_bp, url_prefix='/admin/products')
        print("✅ [Registry]: تم تسجيل موديول 'إدارة المنتجات' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'إدارة المنتجات': {e}")

# 2. الاستيرادات في نهاية الملف (لضمان ربط جميع المسارات بالـ Blueprint)
# تم إضافة routes هنا لضمان أن دالة manage_products تعمل عند التشغيل
from . import routes, routes_add, routes_edit, routes_sync
