# coding: utf-8
# 📂 apps/admin_suppliers_add/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from apps.models.supplier_db import Supplier
from apps.extensions import db

# نستخدم الاسم الجديد للـ Blueprint
admin_suppliers_add_bp = Blueprint(
    'admin_suppliers_add', 
    __name__, 
    template_folder='templates'
)

@admin_suppliers_add_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        # ... (نفس منطق الحفظ السابق) ...
        # تأكد من استدعاء اسم الموديل الصحيح هنا
        pass
        
    return render_template('admin_suppliers_add/admin_suppliers_add.html')
