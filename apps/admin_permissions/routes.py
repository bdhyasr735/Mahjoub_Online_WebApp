# coding: utf-8
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
import secrets
import string

from apps.extensions import db
from apps.models.admin_staff_db import AdminStaff
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.suppliers_db import Supplier  # استيراد جدول الموردين

admin_permissions_bp = Blueprint('admin_permissions', __name__, template_folder='templates')

def is_admin():
    return current_user.is_authenticated and (getattr(current_user, 'role', '') in ['admin', 'Owner'])

def generate_random_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

@admin_permissions_bp.route('/admin/permissions/roles', methods=['GET'])
@login_required
def roles_list():
    if not is_admin():
        return redirect(url_for('admin_dashboard.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    staff_type = request.args.get('type', 'admin')
    
    model = AdminStaff if staff_type == 'admin' else SupplierStaff
    query = model.query
    
    if search:
        query = query.filter(model.username.contains(search) | model.phone.contains(search))
        
    pagination = query.order_by(model.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    
    # جلب قائمة الموردين لعرضها في القائمة المنسدلة للمودال
    all_suppliers = Supplier.query.all()
    
    return render_template('admin/permissions.html', 
                           staff=pagination.items, 
                           pagination=pagination, 
                           type_filter=staff_type,
                           suppliers=all_suppliers)

@admin_permissions_bp.route('/admin/permissions/assign', methods=['POST'])
@login_required
def assign_permissions():
    if not is_admin(): return redirect(url_for('admin_dashboard.dashboard'))
    
    username = request.form.get('username')
    phone = request.form.get('phone')
    staff_type = request.form.get('type')
    supplier_id = request.form.get('supplier_id') # التقاط المورد المختار
    
    if username and phone:
        if staff_type == 'admin':
            new_staff = AdminStaff(username=username, phone=phone, role='worker')
        else:
            # التأكد من وجود supplier_id عند اختيار موظف شريك
            if not supplier_id:
                flash("يجب اختيار مورد تابع له الموظف", "danger")
                return redirect(url_for('admin_permissions.roles_list', type='supplier'))
            
            new_staff = SupplierStaff(username=username, phone=phone, role='worker', supplier_id=int(supplier_id))
        
        new_staff.set_password('123456')
        db.session.add(new_staff)
        db.session.commit()
        flash(f"تمت إضافة {username} بنجاح", "success")
    
    return redirect(url_for('admin_permissions.roles_list', type=staff_type))

# ... دوال reset_password و toggle_status كما هي ...
