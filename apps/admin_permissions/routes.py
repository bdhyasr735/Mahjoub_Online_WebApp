# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models import AdminStaff, Supplier, SupplierStaff  # تأكد من استيراد SupplierStaff
from apps.admin_permissions.registry import ADMIN_PERMISSIONS_REGISTRY, SUPPLIER_PERMISSIONS_REGISTRY

admin_permissions_bp = Blueprint('admin_permissions', __name__, template_folder='templates')

@admin_permissions_bp.route('/', methods=['GET'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    staff_type = request.args.get('staff_type', 'admin_staff')
    
    user_scope = 'admin' if getattr(current_user, 'is_admin', True) else 'supplier'

    if staff_type == 'admin_staff':
        pagination = AdminStaff.query.order_by(AdminStaff.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
        staff_list = pagination.items
        perm_dict = ADMIN_PERMISSIONS_REGISTRY
    else:
        # افتراض وجود نموذج SupplierStaff
        pagination = SupplierStaff.query.order_by(SupplierStaff.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
        staff_list = pagination.items
        perm_dict = SUPPLIER_PERMISSIONS_REGISTRY

    return render_template(
        'admin/permissions.html',
        user_scope=user_scope,
        staff_list=staff_list,
        staff_type=staff_type,
        pagination=pagination,
        admin_permissions_list=ADMIN_PERMISSIONS_REGISTRY,
        supplier_permissions_list=SUPPLIER_PERMISSIONS_REGISTRY,
        suppliers=Supplier.query.all()
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

        # التحقق من المدخلات
        if not username or not name or not password:
            return jsonify({'status': 'error', 'message': 'بيانات الموظف غير مكتملة.'}), 400

        # منطق الإضافة حسب النوع
        if staff_type == 'admin_staff':
            new_staff = AdminStaff(name=name, username=username, phone=phone, email=email, permissions={})
            new_staff.set_password(password)
            db.session.add(new_staff)
        
        elif staff_type == 'supplier_staff':
            if not supplier_id:
                return jsonify({'status': 'error', 'message': 'يجب تحديد المورد.'}), 400
            
            new_staff = SupplierStaff(
                name=name, username=username, phone=phone, email=email, 
                supplier_id=supplier_id, permissions={}
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
    # تحقق في كلا الجدولين لمنع التكرار الشامل
    exists = AdminStaff.query.filter_by(**{field: value}).first() is not None or \
             SupplierStaff.query.filter_by(**{field: value}).first() is not None
    return jsonify({'exists': exists})

@admin_permissions_bp.route('/staff/<int:target_id>/update-permissions', methods=['POST'])
@login_required
def update_permissions(target_id):
    # ملاحظة: يجب تعديل هذا المسار ليدعم التمييز بين AdminStaff و SupplierStaff
    staff = AdminStaff.query.get_or_404(target_id)
    perms = {k.replace('perm_', ''): True for k in request.form if k.startswith('perm_')}
    staff.permissions = perms
    db.session.commit()
    return redirect(url_for('admin_permissions.index'))
