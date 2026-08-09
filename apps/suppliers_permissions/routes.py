# -*- coding: utf-8 -*-
# 📂 apps/supplier_permissions/routes.py

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import secrets
import string

from apps.supplier_permissions import supplier_perms_bp
from apps.supplier_permissions.registry import (
    SUPPLIER_PERMISSIONS_REGISTRY,
    DEFAULT_WORKER_PERMISSIONS,
    DEFAULT_MANAGER_PERMISSIONS
)
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.extensions import db


def generate_temp_password(length=10):
    alphabet = string.ascii_letters + string.digits + "!@#$%*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@supplier_perms_bp.route('/', methods=['GET'])
@login_required
def index():
    """عرض الصفحة الرئيسية لإدارة صلاحيات وموظفي المورد"""
    supplier_id = getattr(current_user, 'id', 1)
    
    page = request.args.get('page', 1, type=int)
    current_filter = request.args.get('filter', 'all')
    search_query = request.args.get('search', '').strip()
    per_page = 10
    
    query = SupplierStaff.query.filter_by(supplier_id=supplier_id)
    
    # تطبيق الفلاتر عند النقر
    if current_filter == 'active':
        query = query.filter_by(is_active=True)
    elif current_filter == 'wallet':
        query = query.filter_by(can_view_wallet=True)
    elif current_filter == 'orders':
        query = query.filter_by(can_manage_orders=True)

    if search_query:
        query = query.filter(
            (SupplierStaff.name.ilike(f'%{search_query}%')) |
            (SupplierStaff.username.ilike(f'%{search_query}%')) |
            (SupplierStaff.role_title.ilike(f'%{search_query}%'))
        )
    
    pagination = query.order_by(SupplierStaff.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
        
    staff_list = pagination.items
    
    # الإحصائيات الإجمالية للحساب
    all_staff = SupplierStaff.query.filter_by(supplier_id=supplier_id).all()
    total_staff = len(all_staff)
    active_staff = sum(1 for s in all_staff if s.is_active)
    wallet_staff = sum(1 for s in all_staff if s.can_view_wallet)
    orders_staff = sum(1 for s in all_staff if s.can_manage_orders)

    return render_template(
        'supplier_perms/supplier_permissions.html',
        staff_list=staff_list,
        pagination=pagination,
        current_filter=current_filter,
        search_query=search_query,
        total_staff=total_staff,
        active_staff=active_staff,
        wallet_staff=wallet_staff,
        orders_staff=orders_staff,
        permissions_registry=SUPPLIER_PERMISSIONS_REGISTRY,
        brand_color='#4A154B'
    )


@supplier_perms_bp.route('/api/staff', methods=['GET', 'POST'])
@login_required
def handle_staff():
    """جلب أو إضافة موظف جديد لمورد معين"""
    supplier_id = getattr(current_user, 'id', 1)

    if request.method == 'GET':
        staff_members = SupplierStaff.query.filter_by(supplier_id=supplier_id).all()
        return jsonify({
            'status': 'success',
            'data': [s.to_dict() for s in staff_members]
        })

    if request.method == 'POST':
        data = request.form or request.get_json() or {}
        
        name = data.get('name')
        username = data.get('username')
        phone = data.get('phone')
        email = data.get('email')
        role = data.get('role', 'worker')
        role_title = data.get('role_title', 'موظف مورد')
        can_view_wallet = str(data.get('can_view_wallet')).lower() in ['true', '1', 'on']
        can_manage_orders = str(data.get('can_manage_orders')).lower() in ['true', '1', 'on']

        if not username or not name:
            return jsonify({'status': 'error', 'message': 'يرجى إدخال اسم الموظف واسم المستخدم'}), 400

        # التحقق من عدم تكرار اسم المستخدم لنفس المورد
        existing = SupplierStaff.query.filter_by(supplier_id=supplier_id, username=username).first()
        if existing:
            return jsonify({'status': 'error', 'message': 'اسم المستخدم مستخدم بالفعل في حسابك'}), 400

        temp_password = generate_temp_password(10)

        # تحديد الصلاحيات الافتراضية
        initial_perms = DEFAULT_MANAGER_PERMISSIONS if role == 'manager' else DEFAULT_WORKER_PERMISSIONS

        new_staff = SupplierStaff(
            supplier_id=supplier_id,
            name=name,
            username=username,
            phone=phone,
            email=email,
            role=role,
            role_title=role_title,
            is_active=True,
            can_view_wallet=can_view_wallet,
            can_manage_orders=can_manage_orders,
            permissions=initial_perms
        )
        new_staff.set_password(temp_password)

        try:
            db.session.add(new_staff)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': 'تم إضافة الموظف بنجاح',
                'credentials': {
                    'username': username,
                    'password': temp_password,
                    'name': name
                },
                'staff': new_staff.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'حدث خطأ أثناء الحفظ: {str(e)}'}), 500


@supplier_perms_bp.route('/api/staff/<int:staff_id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(staff_id):
    """تنشيط أو إيقاف حساب موظف المورد"""
    supplier_id = getattr(current_user, 'id', 1)
    staff = SupplierStaff.query.filter_by(id=staff_id, supplier_id=supplier_id).first_or_404()

    staff.is_active = not staff.is_active
    db.session.commit()

    return jsonify({
        'status': 'success',
        'is_active': staff.is_active,
        'message': 'تم تغيير حالة الحساب بنجاح'
    })


@supplier_perms_bp.route('/api/staff/<int:staff_id>/permissions', methods=['POST'])
@login_required
def update_permissions(staff_id):
    """تحديث جدول صلاحيات الموظف التفصيلية"""
    supplier_id = getattr(current_user, 'id', 1)
    staff = SupplierStaff.query.filter_by(id=staff_id, supplier_id=supplier_id).first_or_404()

    data = request.get_json() or {}
    new_perms = data.get('permissions', {})
    
    staff.permissions = new_perms
    staff.can_view_wallet = 'view_wallet' in new_perms.get('financials', [])
    staff.can_manage_orders = 'process_orders' in new_perms.get('orders', [])

    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'تم تحديث الصلاحيات بنجاح',
        'permissions': staff.permissions
    })


@supplier_perms_bp.route('/api/staff/<int:staff_id>/reset-password', methods=['POST'])
@login_required
def reset_password(staff_id):
    """إعادة تعيين كلمة مرور الموظف وتوليد كلمة مرور مؤقتة جديدة"""
    supplier_id = getattr(current_user, 'id', 1)
    staff = SupplierStaff.query.filter_by(id=staff_id, supplier_id=supplier_id).first_or_404()

    new_temp_pass = generate_temp_password(10)
    staff.set_password(new_temp_pass)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'تم إعادة تعيين كلمة المرور بنجاح',
        'credentials': {
            'username': staff.username,
            'password': new_temp_pass,
            'name': staff.name or staff.username
        }
    })


@supplier_perms_bp.route('/api/staff/<int:staff_id>/delete', methods=['POST', 'DELETE'])
@login_required
def delete_staff(staff_id):
    """حذف حساب الموظف نهائياً"""
    supplier_id = getattr(current_user, 'id', 1)
    staff = SupplierStaff.query.filter_by(id=staff_id, supplier_id=supplier_id).first_or_404()

    db.session.delete(staff)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'تم حذف الموظف بنجاح'
    })
