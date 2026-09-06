# -*- coding: utf-8 -*-
# 📂 apps/routes/supplier_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
# (تأكد من استيراد نماذج المنتجات والموظفين حسب مشروعك الفعلي)
# from apps.models.product_db import ProductSupplierMapping
# from apps.models.staff_db import SupplierStaff

supplier_bp = Blueprint('supplier', __name__, url_prefix='/supplier')

@supplier_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة تحكم المورد الرئيسية - محجوب أونلاين"""
    
    # 1. بيانات المورد الحالي (current_user هو كائن Supplier)
    supplier = current_user
    
    # 2. جلب المحفظة المرتبطة بالمورد
    wallet = supplier.wallet
    balance = wallet.balance if wallet else 0.00
    
    # 3. جلب الملف الشخصي المرتبط (للحصول على المدينة مثلاً)
    profile = supplier.supplier_profile
    
    # 4. عداد المنتجات النشطة (يمكن تعديله حسب نموذج المنتجات لديك)
    # مثال: products_count = ProductSupplierMapping.query.filter_by(supplier_id=supplier.id, status='active').count()
    products_count = supplier.product_mappings.count() if hasattr(supplier, 'product_mappings') else 0
    
    # 5. عداد فريق العمل / الموظفين
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
