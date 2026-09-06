# -*- coding: utf-8 -*-
# 📂 apps/suppliers_dashboard/registry.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_profile_db import SupplierProfile
from apps.models.wallet_db import SupplierWallet

# 📊 [المتطلبات التعريفية للتسجيل الديناميكي]
MODULE_NAME = "لوحة تحكم الموردين"
ICON = "fa-tachometer-alt"
SHOW_IN_SUPPLIER = True

NAV_ITEMS = [
    {"endpoint": "suppliers_dashboard.dashboard", "title": "الرئيسية"}
]

# تعريف الـ Blueprint الخاص بلوحة تحكم الموردين مع تحديد مسار القوالب (Templates) وملفات الـ Static إن وجدت
suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    url_prefix='/supplier',
    template_folder='templates',
    static_folder='static'
)


@suppliers_dashboard_bp.route('/dashboard', methods=['GET'], strict_slashes=False)
@login_required
def dashboard():
    """لوحة التحكم الرئيسية للمورد - عرض المؤشرات الحية والمحفظة والبيانات الأساسية"""
    
    # المورد الحالي المسجل دخوله عبر Flask-Login
    supplier = current_user
    
    # جلب المحفظة المرتبطة بالمورد (مع قيمة افتراضية صفرية في حال عدم وجودها)
    wallet = supplier.wallet if hasattr(supplier, 'wallet') else None
    balance = wallet.balance if wallet else 0.00
    
    # جلب الملف الشخصي المرتبط بالمورد (للحصول على معلومات مثل المدينة وغيرها)
    profile = getattr(supplier, 'supplier_profile', None)
    
    # حساب عدد المنتجات النشطة المرتبطة بالمورد
    products_count = supplier.product_mappings.count() if hasattr(supplier, 'product_mappings') else 0
    
    # حساب عدد الموظفين / فريق العمل التابع للمورد
    staff_count = len(supplier.staff_members) if hasattr(supplier, 'staff_members') else 0

    return render_template(
        'suppliers/dashboard.html',
        supplier=supplier,
        wallet=wallet,
        balance=balance,
        profile=profile,
        products_count=products_count,
        staff_count=staff_count
    )


# دالة تسجيل الـ Blueprint في تطبيق Flask الرئيسي (App Factory Pattern)
def init_app(app):
    """تسجيل وحدة لوحة تحكم الموردين في التطبيق الرئيسي"""
    if 'suppliers_dashboard' not in app.blueprints:
        app.register_blueprint(suppliers_dashboard_bp)
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_dashboard' بنجاح.")

def register_module(app):
    init_app(app)
