# coding: utf-8
# 📂 apps/suppliers_permissions/routes.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
import uuid

suppliers_permissions_bp = Blueprint(
    'suppliers_permissions', 
    __name__, 
    template_folder='templates'
)

def check_supplier_owner_access():
    """تحقق أمني صارم لضمان أن الحساب الحالي هو المورد المالك"""
    return session.get('user_type') == 'supplier' and current_user.__class__.__name__ != 'AdminUser'

@suppliers_permissions_bp.route('/', methods=['GET', 'POST'])
@suppliers_permissions_bp.route('/permissions', methods=['GET', 'POST'])
@login_required
def permissions():
    if not check_supplier_owner_access():
        flash("عذراً، هذه الصلاحية متاحة فقط للمورد.", "danger")
        return redirect(url_for('suppliers_dashboard.dashboard'))
        
    supplier = db.session.get(Supplier, current_user.id)
    new_staff_data = None

    if request.method == 'POST':
        # منطق إضافة موظف جديد
        username = request.form.get('username', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        
        if username and phone and password:
            if SupplierStaff.query.filter((SupplierStaff.username == username) | (SupplierStaff.search_phone == phone)).first():
                flash("اسم المستخدم أو الهاتف مسجل مسبقاً.", "danger")
            else:
                new_staff = SupplierStaff(
                    supplier_id=supplier.id,
                    username=username,
                    search_phone=phone,
                    can_view_wallet='can_view_wallet' in request.form,
                    can_manage_orders='can_manage_orders' in request.form,
                    can_manage_settings='can_manage_settings' in request.form,
                    is_active=True
                )
                new_staff.set_password(password)
                new_staff.raw_password = password # للاستخدام في المودال فقط
                db.session.add(new_staff)
                db.session.commit()
                new_staff_data = new_staff
                flash("تمت إضافة الموظف بنجاح.", "success")

    staff_list = SupplierStaff.query.filter_by(supplier_id=supplier.id).all()
    return render_template('suppliers/permissions.html', supplier=supplier, staff_list=staff_list, new_staff=new_staff_data)

@suppliers_permissions_bp.route('/action/<int:staff_id>/<action>', methods=['POST'])
@login_required
def staff_action(staff_id, action):
    """التحكم في إجراءات الموظفين (إيقاف/تفعيل، إعادة تعيين كلمة مرور)"""
    if not check_supplier_owner_access():
        return redirect(url_for('suppliers_dashboard.dashboard'))
        
    staff = SupplierStaff.query.filter_by(id=staff_id, supplier_id=current_user.id).first_or_404()

    if action == 'toggle_status':
        staff.is_active = not staff.is_active
        flash(f"تم {'تفعيل' if staff.is_active else 'إيقاف'} حساب الموظف.", "success")
        
    elif action == 'reset_password':
        new_pass = str(uuid.uuid4())[:8] # توليد كلمة مرور عشوائية
        staff.set_password(new_pass)
        flash(f"تم إعادة تعيين كلمة المرور بنجاح: {new_pass}", "info")

    db.session.commit()
    return redirect(url_for('suppliers_permissions.permissions'))
