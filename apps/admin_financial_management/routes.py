# coding: utf-8
# 📂 apps/admin_suppliers_list/routes.py

from flask import Blueprint, render_template
from flask_login import login_required
from apps.models import Supplier

# تعريف البلوبرنت
suppliers_bp = Blueprint(
    'suppliers_bp', 
    __name__, 
    template_folder='templates'
)

@suppliers_bp.route('/list', methods=['GET'])
@login_required
def list_suppliers():
    """عرض قائمة الموردين/الشركاء في المنصة."""
    suppliers = Supplier.query.order_by(Supplier.created_at.desc()).all()
    
    return render_template(
        'admin_suppliers_list/list.html', 
        suppliers=suppliers
    )

@suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """صفحة إضافة مورد جديد."""
    return render_template('admin_suppliers_list/add.html')
