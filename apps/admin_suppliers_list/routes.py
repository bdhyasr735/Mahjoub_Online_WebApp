# coding: utf-8
# 📂 apps/admin_suppliers_list/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.models import Supplier
from apps.extensions import db

# تعريف البلوبرنت
suppliers_bp = Blueprint(
    'suppliers_bp', 
    __name__, 
    template_folder='templates',
    url_prefix='/admin/suppliers' # تمت إضافته هنا كحماية إضافية
)

@suppliers_bp.route('/list', methods=['GET'])
@login_required
def list_suppliers():
    """عرض قائمة الموردين/الشركاء في المنصة."""
    try:
        # جلب جميع الموردين مرتبين حسب الأحدث
        suppliers = Supplier.query.order_by(Supplier.created_at.desc()).all()
    except Exception as e:
        suppliers = []
        print(f"⚠️ خطأ أثناء جلب الموردين: {e}")
    
    return render_template(
        'admin_suppliers_list/list.html', 
        suppliers=suppliers
    )

@suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """صفحة إضافة مورد جديد."""
    # يمكنك هنا إضافة منطق المعالجة (POST) إذا لزم الأمر
    return render_template('admin_suppliers_list/add.html')

@suppliers_bp.route('/<int:supplier_id>/details', methods=['GET'])
@login_required
def supplier_details(supplier_id):
    """عرض تفاصيل مورد معين."""
    supplier = Supplier.query.get_or_404(supplier_id)
    return render_template('admin_suppliers_list/details.html', supplier=supplier)
