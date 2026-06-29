# coding: utf-8
# 📂 apps/suppliers_list/routes.py

from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy.orm import joinedload
from apps.models.supplier_db import Supplier

# تعريف الـ Blueprint الخاص بموديول الشركاء
# لاحظ أننا نستخدم اسم المجلد كاسم للـ template_folder
supplier_bp = Blueprint(
    'supplier_app', 
    __name__, 
    template_folder='templates'
)

@supplier_bp.route('/list', methods=['GET'])
@login_required
def list_suppliers():
    """
    عرض قائمة بجميع الشركاء/الموردين المسجلين في النظام.
    يتم استخدام joinedload لجلب البيانات المرتبطة (Profile & Staff)
    في استعلام واحد لتحسين الأداء (Eager Loading).
    """
    
    # جلب جميع الشركاء مرتبين من الأحدث للأقدم مع بياناتهم المرتبطة
    suppliers = Supplier.query.options(
        joinedload(Supplier.supplier_profile),
        joinedload(Supplier.staff_members)
    ).order_by(Supplier.created_at.desc()).all()
    
    return render_template(
        'suppliers_list/suppliers_list.html', 
        suppliers=suppliers
    )
