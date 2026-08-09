# -*- coding: utf-8 -*-
# 📂 apps/suppliers_permissions/routes.py

from flask import render_template, request, jsonify, flash, redirect, url_for, session
from flask_login import login_required, current_user
import secrets
import string

from apps.suppliers_permissions import suppliers_permissions_bp
from apps.suppliers_permissions.registry import (
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


@suppliers_permissions_bp.route('/', methods=['GET'])
@login_required
def index():
    """عرض الصفحة الرئيسية لإدارة صلاحيات وموظفي المورد بنظام الحاويات المتجاوبة والتحمل العالي"""
    supplier_id = getattr(current_user, 'id', 1)
    
    page = request.args.get('page', 1, type=int)
    current_filter = request.args.get('filter', 'all')
    search_query = request.args.get('search', '').strip()
    
    # ضبط عدد العناصر ليناسب شبكة الحاويات (Grid) 3 عناصر في كل صف للشاشات الكبيرة
    per_page = 12
    
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
    
    # جلب الصفحة المطلوبة فقط من قاعدة البيانات لتوفير الذاكرة وتحمل الضغط العالي
    pagination = query.order_by(SupplierStaff.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
        
    staff_list = pagination.items
    
    # الإحصائيات الإجمالية للحساب
    all_staff = SupplierStaff.query.filter_by(supplier_id=supplier_id).all()
    total_staff = len(all_staff)
    active_staff = sum(1 for s in all_staff if s.is_active)
    wallet_staff = sum(1 for s in all_staff if s.can_view_wallet)
    orders_staff = sum(1 for s in all_staff if s.can_manage_orders)

    # جلب بيانات الاعتماد المؤقتة من الجلسة (إن وجدت لمرة واحدة) ثم حذفها
    new_staff_credentials = session.pop('new_staff_credentials', None)

    return render_template(
        'suppliers/permissions.html',
        staff_list=staff_list,
        pagination=pagination,
        current_filter=current_filter,
        search_query=search_query,
        total_staff=total_staff,
        active_staff=active_staff,
        wallet_staff=wallet_staff,
        orders_staff=orders_staff,
        permissions_registry=SUPPLIER_PERMISSIONS_REGISTRY,
        brand_color='#4A154B',
        new_staff_credentials=new_staff_credentials
    )


@suppliers_permissions_bp.route('/staff/add', methods=['POST'])
@login_required
def add_staff():
    """إضافة موظف جديد عبر نموذج تقليدي من الواجهة"""
    supplier_id = getattr(current_user, 'id', 1)
    
    name = request.form.get('name')
    username = request.form.get('username')
    phone = request.form.get('phone')
    email = request.form.get('email')
    role = request.form.get('role', 'worker')
    role_title = request.form.get('role_title', 'موظف مورد')
    
    if not username:
        flash('يرجى إدخال اسم المستخدم الأساسي للدخول.', 'error')
        return redirect(url_for('suppliers_permissions_bp.index'))

    existing = SupplierStaff.query.filter_by(supplier_id=supplier_id, username=username).first()
    if existing:
        flash('اسم المستخدم مستخدم بالفعل، يرجى اختيار اسم مستخدم آخر.', 'error')
        return redirect(url_for('suppliers_permissions_bp.index'))

    temp_password = generate_temp_password(10)
    initial_perms = DEFAULT_MANAGER_PERMISSIONS if role == 'manager' else DEFAULT_WORKER_PERMISSIONS

    new_staff = SupplierStaff(
        supplier_id=supplier_id,
        name=name or username,
        username=username,
        phone=phone,
        email=email,
        role=role,
        role_title=role_title,
        is_active=True,
        can_view_wallet=False,
        can_manage_orders=False,
        permissions=initial_perms
    )
    new_staff.set_password(temp_password)

    try:
        db.session.add(new_staff)
        db.session.commit()

        # تخزين بيانات الاعتماد في الجلسة لعرضها في النافذة المنبثقة لمرة واحدة
        session['new_staff_credentials'] = {
            'name': new_staff.name,
            'username': username,
            'password': temp_password
        }
        flash('تم إضافة الموظف بنجاح.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حفظ الموظف: {str(e)}', 'error')

    return redirect(url_for('suppliers_permissions_bp.index'))


@suppliers_permissions_bp.route('/staff/<int:staff_id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(staff_id):
    """تنشيط أو إيقاف حساب موظف المورد"""
    supplier_id = getattr(current_user, 'id', 1)
    staff = SupplierStaff.query.filter_by(id=staff_id, supplier_id=supplier_id).first_or_404()

    staff.is_active = not staff.is_active
    db.session.commit()

    flash('تم تغيير حالة حساب الموظف بنجاح.', 'success')
    return redirect(url_for('suppliers_permissions_bp.index'))


@suppliers_permissions_bp.route('/staff/<int:staff_id>/permissions', methods=['POST'])
@login_required
def update_permissions(staff_id):
    """تحديث جدول صلاحيات الموظف التفصيلية عبر النماذج التقليدية"""
    supplier_id = getattr(current_user, 'id', 1)
    staff = SupplierStaff.query.filter_by(id=staff_id, supplier_id=supplier_id).first_or_404()

    can_manage_wallet = request.form.get('can_manage_wallet') == 'y'
    can_manage_orders = request.form.get('can_manage_orders') == 'y'

    staff.can_view_wallet = can_manage_wallet
    staff.can_manage_orders = can_manage_orders

    db.session.commit()

    flash('تم تحديث صلاحيات الموظف بنجاح.', 'success')
    return redirect(url_for('suppliers_permissions_bp.index'))


@suppliers_permissions_bp.route('/staff/<int:staff_id>/reset-password', methods=['POST'])
@login_required
def reset_password(staff_id):
    """إعادة تعيين كلمة مرور الموظف وتوليد كلمة مرور مؤقتة جديدة وتخزينها بالجلسة"""
    supplier_id = getattr(current_user, 'id', 1)
    staff = SupplierStaff.query.filter_by(id=staff_id, supplier_id=supplier_id).first_or_404()

    new_temp_pass = generate_temp_password(10)
    staff.set_password(new_temp_pass)
    db.session.commit()

    session['new_staff_credentials'] = {
        'name': staff.name or staff.username,
        'username': staff.username,
        'password': new_temp_pass
    }

    flash('تم إعادة تعيين كلمة المرور بنجاح.', 'success')
    return redirect(url_for('suppliers_permissions_bp.index'))


# بقية مسارات الـ API القديمة لدعم التطبيقات الخارجية أو الواجهات البرمجية (إن وجدت)
@suppliers_permissions_bp.route('/api/staff', methods=['GET', 'POST'])
@login_required
def handle_staff_api():
    supplier_id = getattr(current_user, 'id', 1)
    if request.method == 'GET':
        staff_members = SupplierStaff.query.filter_by(supplier_id=supplier_id).all()
        return jsonify({
            'success': True,
            'data': [s.to_dict() for s in staff_members]
        })
    return jsonify({'success': False, 'message': 'Not supported via JSON API'}), 400
