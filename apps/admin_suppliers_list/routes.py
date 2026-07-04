# 📂 apps/admin_suppliers_list/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required
from apps.models import Supplier
from apps.extensions import db

# تعريف البلوبرينت
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
        current_app.logger.error(f"⚠️ خطأ أثناء جلب الموردين: {e}")
        flash("حدث خطأ أثناء تحميل قائمة الموردين.", "danger")
    
    return render_template(
        'admin_suppliers_list/admin_suppliers_list.html', 
        suppliers=suppliers
    )

@suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """صفحة إضافة مورد جديد مع معالجة البيانات."""
    if request.method == 'POST':
        try:
            # هنا يمكنك إضافة logic الإضافة (استلام البيانات من النموذج)
            # مثال: name = request.form.get('name')
            # db.session.add(new_supplier)
            # db.session.commit()
            flash("تم استلام طلب الإضافة (يجب ربط النموذج بقاعدة البيانات).", "info")
            return redirect(url_for('suppliers_bp.list_suppliers'))
        except Exception as e:
            current_app.logger.error(f"⚠️ خطأ أثناء إضافة المورد: {e}")
            flash("حدث خطأ أثناء حفظ المورد.", "danger")

    return render_template('admin_suppliers_list/add.html')

@suppliers_bp.route('/<int:supplier_id>/details', methods=['GET'])
@login_required
def supplier_details(supplier_id):
    """عرض تفاصيل مورد معين."""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        return render_template('admin_suppliers_list/details.html', supplier=supplier)
    except Exception as e:
        current_app.logger.error(f"⚠️ خطأ أثناء عرض تفاصيل المورد {supplier_id}: {e}")
        flash("المورد المطلوب غير موجود.", "warning")
        return redirect(url_for('suppliers_bp.list_suppliers'))
