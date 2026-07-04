# coding: utf-8
# 📂 apps/admin_suppliers_list/routes.py

from flask import Blueprint, render_template
from flask_login import login_required
from apps.models.supplier_db import Supplier

# تعريف الـ Blueprint
suppliers_bp = Blueprint(
    'suppliers_bp', 
    __name__, 
    template_folder='templates'
)

@suppliers_bp.route('/list')
@login_required
def list_suppliers():
    # جلب الموردين وعرضهم في الصفحة
    suppliers = Supplier.query.order_by(Supplier.id.desc()).all()
    return render_template('admin_suppliers_list/admin_suppliers_list.html', suppliers=suppliers)
