# coding: utf-8
# 📂 apps/admin_Product/registry.py

import apps.admin_Product.routes as product_routes
import apps.admin_Product.routes_edit as product_edit_routes

# بيانات الموديول للظهور في الشريط الجانبي
MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fa-boxes"
SHOW_IN_SUPPLIER = False

# هنا المفتاح هو الـ endpoint (اسم المسار)، والقيمة هي النص العربي الذي سيظهر في القائمة
LINKS = {
    "admin_product_bp.manage_products": "المنتجات",
    "admin_product_bp.add_product": "إضافة منتج"
    # زر المزامنة سيبقى داخل نافذة إدارة المنتجات (Modal) ولا يظهر هنا
}

def register_module(app):
    # تسجيل الـ Blueprint (بما أن مسارات الإدارة والتعديل تشترك في نفس اسم الـ Blueprint admin_product_bp،
    # يكفي تسجيله من الملف الأساسي أو ملف التعديل بشرط أن يكونا مستخدمين لنفس الـ Blueprint)
    app.register_blueprint(product_routes.admin_product_bp)
