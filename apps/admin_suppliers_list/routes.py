# coding: utf-8
# 📂 apps/admin_suppliers_list/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.models import Supplier  # الاستيراد من الواجهة الموحدة
from apps.extensions import db

# تعريف البلوبرينت
# ملاحظة: تمت إزالة url_prefix من هنا لأننا نحدده في registry.py عند تسجيل الموديول
suppliers_bp = Blueprint(
    'suppliers_bp', 
    __name__, 
    template_folder='templates'
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
    
    # تأكد من أن المسار في الـ render_template يطابق هيكل مجلد الـ templates عندك
    return render_template(
        'admin_suppliers_list/admin_suppliers_list.html', 
        suppliers=suppliers
    )

@suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """صفحة إضافة مورد جديد."""
    return render_template('admin_suppliers_list/add.html')

@suppliers_bp.route('/<int:supplier_id>/details', methods=['GET'])
@login_required
def supplier_details(supplier_id):
    """عرض تفاصيل مورد معين."""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        return render_template('admin_suppliers_list/details.html', supplier=supplier)
    except Exception as e:
        flash("حدث خطأ أثناء جلب تفاصيل المورد.")
        return redirect(url_for('suppliers_bp.list_suppliers'))
