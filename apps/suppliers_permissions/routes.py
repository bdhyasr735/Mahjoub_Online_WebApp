# coding: utf-8
# 📂 apps/suppliers_permissions/routes.py

import secrets
import string
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff

# تعريف الـ Blueprint
suppliers_permissions_bp = Blueprint(
    'suppliers_permissions', 
    __name__, 
    template_folder='templates'
)

# دالة للتحقق من صلاحية المالك
def check_supplier_owner_access():
    return session.get('user_type') == 'supplier'

# دالة لتوليد كلمة مرور عشوائية قوية
def generate_random_password(length=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

# --- المسار الرئيسي لإدارة الصلاحيات ---
@suppliers_permissions_bp.route('/permissions', methods=['GET', 'POST'])
@login_required
def permissions():
    if not check_supplier_owner_access():
        return redirect(url_for('suppliers_dashboard.dashboard'))
    
    supplier = db.session.get(Supplier, current_user.id)
    # جلب الموظفين التابعين للمورد الحالي فقط
    staff_list = SupplierStaff.query.filter_by(supplier_id=supplier.id).order_by(SupplierStaff.created_at.desc()).all()
    
    return render_template('suppliers/permissions.html', supplier=supplier, staff_list=staff_list)

# --- المسار للتحقق اللحظي من توفر البيانات ---
@suppliers_permissions_bp.route('/check-availability', methods=['POST'])
@login_required
def check_availability():
    data = request.get_json()
    field = data.get('field')  # 'username' أو 'phone'
    value = data.get('value')
    
    query = SupplierStaff.query.filter_by(supplier_id=current_user.id)
    if field == 'username':
        exists = query.filter_by(username=value).first()
    elif field == 'phone':
        # البحث عن آخر 9 أرقام للهاتف
        exists = query.filter_by(search_phone=str(value)[-9:]).first()
    else:
        return jsonify({"available": False}), 400
        
    return jsonify({"available": not exists})

# --- المسار لإضافة موظف جديد عبر AJAX ---
@suppliers_permissions_bp.route('/add-staff', methods=['POST'])
@login_required
def add_staff():
    if not check_supplier_owner_access():
        return jsonify({"success": False, "message": "غير مصرح"})
    
    username = request.form.get('username')
    phone = request.form.get('phone')
    password = generate_random_password()
    
    new_staff = SupplierStaff(
        supplier_id=current_user.id,
        username=username,
        search_phone=str(phone)[-9:],
        is_active=True,
        can_view_wallet=('can_view_wallet' in request.form),
        can_manage_orders=('can_manage_orders' in request.form)
    )
    new_staff.set_password(password)
    
    db.session.add(new_staff)
    db.session.commit()
    
    return jsonify({
        "success": True, 
        "username": username, 
        "password": password
    })

# --- المسار لإدارة عمليات الموظفين (تفعيل/إيقاف/تغيير كلمة المرور) ---
@suppliers_permissions_bp.route('/action/<int:staff_id>/<action>', methods=['POST'])
@login_required
def staff_action(staff_id, action):
    # التأكد أن الموظف يتبع المورد الحالي فقط
    staff = SupplierStaff.query.filter_by(id=staff_id, supplier_id=current_user.id).first_or_404()

    if action == 'toggle_status':
        staff.is_active = not staff.is_active
        db.session.commit()
        return jsonify({"success": True, "is_active": staff.is_active})
    
    elif action == 'reset_password':
        new_pass = generate_random_password()
        staff.set_password(new_pass)
        db.session.commit()
        return jsonify({"success": True, "new_password": new_pass})

    return jsonify({"success": False}), 400
