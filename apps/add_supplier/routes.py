# coding: utf-8
# ⚙️ محرك تعميد وإدارة الموردين - منصة محجوب أونلاين 2026

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from . import admin_suppliers_bp
from apps.models.supplier_db import Supplier, db

@admin_suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier_route():
    """
    مسار تعميد مورد جديد - متطابق مع url_for('add_supplier.add_supplier_route')
    """
    if request.method == 'POST':
        # أضف هنا منطق معالجة البيانات
        flash("تم تعميد المورد بنظام السيادة بنجاح", "success")
        return redirect(url_for('add_supplier.add_supplier_route'))
        
    return render_template('add_supplier/add_supplier.html')

@admin_suppliers_bp.route('/list', methods=['GET'])
@login_required
def list_suppliers_data():
    """
    مسار جلب قائمة الموردين
    """
    suppliers = Supplier.query.all()
    return render_template('add_supplier/list.html', suppliers=suppliers)
