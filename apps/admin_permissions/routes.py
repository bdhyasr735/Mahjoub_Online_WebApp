# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models import AdminStaff, Supplier, SupplierStaff
from apps.admin_permissions.registry import ADMIN_PERMISSIONS_REGISTRY, SUPPLIER_PERMISSIONS_REGISTRY

admin_permissions_bp = Blueprint('admin_permissions', __name__, template_folder='templates')

@admin_permissions_bp.route('/', methods=['GET'])
@login_required
def index():
    page_admin = request.args.get('page_admin', 1, type=int)
    page_supplier = request.args.get('page_supplier', 1, type=int)
    staff_type = request.args.get('staff_type', 'admin_staff')
    user_scope = 'admin' if getattr(current_user, 'is_admin', True) else 'supplier'
    admin_pagination = AdminStaff.query.order_by(AdminStaff.created_at.desc()).paginate(page=page_admin, per_page=10, error_out=False)
    supplier_pagination = SupplierStaff.query.order_by(SupplierStaff.created_at.desc()).paginate(page=page_supplier, per_page=10, error_out=False)
    total_admin_staffs = AdminStaff.query.count()
    total_suppliers = Supplier.query.count()
    total_supplier_staffs = SupplierStaff.query.count()
    can_manage = True
    return render_template(
        'admin/permissions.html',
        user_scope=user_scope,
        can_manage=can_manage,
        staff_type=staff_type,
        admin_staffs=admin_pagination.items,
        supplier_staffs=supplier_pagination.items,
        admin_pagination=admin_pagination,
        supplier_pagination=supplier_pagination,
        admin_permissions_list=ADMIN_PERMISSIONS_REGISTRY,
        supplier_permissions_list=SUPPLIER_PERMISSIONS_REGISTRY,
        suppliers=Supplier.query.all(),
        total_admin_staffs=total_admin_staffs,
        total_suppliers=total_suppliers,
        total_supplier_staffs=total_supplier_staffs
    )

@admin_permissions_bp.route('/staff/add', methods=['POST'])
@login_required
def add_staff():
    try:
        staff_type = request.form.get('staff_type', 'admin_staff')
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip() or None
        password = request.form.get('password', '').strip()
        supplier_id = request.form.get('supplier_id')
        role_title = request.form.get('role_title', '').strip()
        if not username or not name or not password:
            return jsonify({'status': 'error', 'message': 'بيانات الموظف غير مكتملة.'}), 400
        perms = {k.replace('perm_', ''): True for k in request.form if k.startswith('perm_')}
        if staff_type == 'admin_staff':
            new_staff = AdminStaff(
                name=name,
                username=username,
                phone=phone,
                email=email,
                role_title=role_title,
                permissions=perms
            )
            new_staff.set_password(password)
            db.session.add(new_staff)
        elif staff_type == 'supplier_staff':
            if not supplier_id:
                return jsonify({'status': 'error', 'message': 'يجب تحديد المورد.'}), 400
            new_staff = SupplierStaff(
                name=name,
                username=username,
                phone=phone,
                email=email,
                role_title=role_title,
                supplier_id=supplier_id,
                permissions=perms
            )
            new_staff.set_password(password)
            db.session.add(new_staff)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'تم إضافة الموظف بنجاح.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_permissions_bp.route('/check-availability', methods=['GET'])
@login_required
def check_availability():
    field = request.args.get('field')
    value = request.args.get('value')
    if not field or not value:
        return jsonify({'exists': False})
    exists = False
    try:
        if field in ['username', 'email', 'phone']:
            filter_args = {field: value}
            exists = (
                AdminStaff.query.filter_by(**filter_args).first() is not None or
                SupplierStaff.query.filter_by(**filter_args).first() is not None
            )
    except Exception as e:
        print(f"Availability Check Error: {e}")
        exists = False
    return jsonify({'exists': exists})

@admin_permissions_bp.route('/staff/<int:target_id>/update-permissions', methods=['POST'])
@login_required
def update_permissions(target_id):
    staff_type = request.form.get('staff_type', 'admin_staff')
    if staff_type == 'admin_staff':
        staff = AdminStaff.query.get_or_404(target_id)
    else:
        staff = SupplierStaff.query.get_or_404(target_id)
    perms = {k.replace('perm_', ''): True for k in request.form if k.startswith('perm_')}
    staff.permissions = perms
    db.session.commit()
    flash('تم تحديث الصلاحيات بنجاح.', 'success')
    return redirect(url_for('admin_permissions.index', staff_type=staff_type))
