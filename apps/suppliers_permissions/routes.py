# coding: utf-8
# 📂 apps/suppliers_permissions/routes.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
import uuid

# تعريف الـ Blueprint
suppliers_permissions_bp = Blueprint(
    'suppliers_permissions', 
    __name__, 
    template_folder='templates'
)

def check_supplier_owner_access():
    """تحقق أمني صارم: فقط المورد المالك يمكنه الوصول"""
    return session.get('user_type') == 'supplier'

@suppliers_permissions_bp.route('/', methods=['GET', 'POST'])
@suppliers_permissions_bp.route('/permissions', methods=['GET', 'POST'])
@login_required
def permissions():
    if not check_supplier_owner_access():
        flash("عذراً، هذه الصلاحية متاحة فقط للمورد المالك.", "danger")
        return redirect(url_for('suppliers_dashboard.dashboard'))
        
    supplier = db.session.get(Supplier, current_user.id)
    new_staff_data = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        
        # إضافة الصلاحيات من الـ form
        can_view_wallet = 'can_view_wallet' in request.form
        can_manage_orders = 'can_manage_orders' in request.form
        
        if username and phone and password:
            if SupplierStaff.query.filter((SupplierStaff.username == username) | (SupplierStaff.search_phone == phone)).first():
                flash("اسم المستخدم أو رقم الهاتف مسجل مسبقاً في النظام.", "danger")
            else:
                new_staff = SupplierStaff(
                    supplier_id=supplier.id,
                    username=username,
                    search_phone=phone,
                    is_active=True,
                    can_view_wallet=can_view_wallet,
                    can_manage_orders=can_manage_orders
                )
                new_staff.set_password(password)
                new_staff.raw_password = password 
                
                db.session.add(new_staff)
                db.session.commit()
                new_staff_data = new_staff
                flash(f"تم إضافة الموظف {username} بنجاح.", "success")

    staff_list = SupplierStaff.query.filter_by(supplier_id=supplier.id).order_by(SupplierStaff.created_at.desc()).all()
    
    return render_template(
        'suppliers/permissions.html', 
        supplier=supplier, 
        staff_list=staff_list, 
        new_staff=new_staff_data
    )

# --- المسار الجديد للتحقق اللحظي ---
@suppliers_permissions_bp.route('/check-availability', methods=['POST'])
@login_required
def check_availability():
    """التحقق اللحظي من توفر اسم المستخدم أو رقم الهاتف"""
    data = request.get_json()
    field = data.get('field')  # 'username' أو 'phone'
    value = data.get('value')
    
    if field == 'username':
        exists = SupplierStaff.query.filter_by(username=value).first()
    elif field == 'phone':
        exists = SupplierStaff.query.filter_by(search_phone=value).first()
    else:
        return jsonify({"available": False}), 400
        
    return jsonify({"available": not exists})

@suppliers_permissions_bp.route('/action/<int:staff_id>/<action>', methods=['POST'])
@login_required
def staff_action(staff_id, action):
    """إدارة عمليات الموظفين (تفعيل/إيقاف، حذف، إعادة تعيين كلمة مرور)"""
    if not check_supplier_owner_access():
        flash("غير مصرح لك بالقيام بهذا الإجراء.", "danger")
        return redirect(url_for('suppliers_dashboard.dashboard'))
        
    staff = SupplierStaff.query.filter_by(id=staff_id, supplier_id=current_user.id).first_or_404()

    if action == 'toggle_status':
        staff.is_active = not staff.is_active
        status_text = "تفعيل" if staff.is_active else "إيقاف"
        flash(f"تم {status_text} حساب الموظف {staff.username} بنجاح.", "success")
        
    elif action == 'reset_password':
        new_pass = str(uuid.uuid4())[:8]
        staff.set_password(new_pass)
        flash(f"تم إعادة تعيين كلمة المرور بنجاح للموظف {staff.username}. الجديدة هي: {new_pass}", "info")
        
    elif action == 'delete':
        db.session.delete(staff)
        flash(f"تم حذف الموظف {staff.username} نهائياً.", "warning")

    db.session.commit()
    return redirect(url_for('suppliers_permissions.permissions'))
