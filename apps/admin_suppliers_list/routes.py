# coding: utf-8
# 📂 apps/admin_suppliers_list/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from apps.models.supplier_db import Supplier
from apps.extensions import db

# تعريف الـ Blueprint
suppliers_bp = Blueprint(
    'suppliers_bp', 
    __name__, 
    template_folder='templates'
)

# تأكد أن أسماء الدوال تطابق ما كتبته في HTML
@suppliers_bp.route('/list')
@login_required
def list_suppliers():
    suppliers = Supplier.query.all()
    return render_template('admin_suppliers_list/admin_suppliers_list.html', suppliers=suppliers)

# مثال لدالة الإضافة (أضف المسارات الأخرى التي تحتاجها)
@suppliers_bp.route('/add')
@login_required
def add_supplier():
    # منطق إضافة المورد
    return "صفحة إضافة المورد"
