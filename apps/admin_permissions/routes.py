# coding: utf-8
# 📂 apps/admin_permissions/routes.py

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
import secrets
import string

from apps.extensions import db
from apps.models.admin_staff_db import AdminStaff
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.supplier_db import Supplier 

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
        flash("غير مصرح لك.", "danger")
        return redirect(url_for('admin_dashboard.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    staff_type = request.args.get('type', 'admin')
    
    # تحديد الموديل بناءً على نوع الموظف
    model = AdminStaff if staff_type == 'admin' else SupplierStaff
    query = model.query
    
    # فلترة البحث
    if search:
        query = query.filter(model.username.contains(search) | model.phone.contains(search))
        
    # الترقيم الصفحي
    pagination = query.order_by(model.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    
    # جلب الموردين للقائمة المنسدلة
    all_suppliers = Supplier.query.all()
    
    return render_template('admin/permissions.html', 
                           staff=pagination.items, 
                           pagination=pagination, 
                           type_filter=staff_type,
                           suppliers=all_suppliers)

@admin_permissions_bp.route('/admin/permissions/assign', methods=['POST'])
@login_required
def assign_permissions():
    """
    ملاحظة: هذا المسار يتطلب وجود CSRF Token في الفورم (HTML)
    بسبب استخدام Flask-WTF أو CSRFProtect في إعدادات التطبيق.
    """
    if not is_admin(): return redirect(url_for('admin_dashboard.dashboard'))
    
    username = request.form.get('username')
    phone = request.form.get('phone')
    staff_type = request.form.get('type')
    supplier_id = request.form.get('supplier_id')
    
    if username and phone:
        if staff_type == 'admin':
            new_staff = AdminStaff(username=username, phone=phone, role='worker')
        else:
            if not supplier_id:
                flash("يجب اختيار مورد تابع له الموظف", "danger")
                return redirect(url_for('admin_permissions.roles_list', type='supplier'))
            
            new_staff = SupplierStaff(username=username, phone=phone, role='worker', supplier_id=int(supplier_id))
        
        new_staff.set_password('123456')
        db.session.add(new_staff)
        db.session.commit()
        flash(f"تمت إضافة {username} بنجاح", "success")
    
    return redirect(url_for('admin_permissions.roles_list', type=staff_type))

@admin_permissions_bp.route('/admin/permissions/reset-password/<int:id>/<string:type>', methods=['GET'])
@login_required
def reset_password(id, type):
    model = AdminStaff if type == 'admin' else SupplierStaff
    staff = model.query.get_or_404(id)
    new_pass = generate_random_password()
    staff.set_password(new_pass)
    db.session.commit()
    flash(f"تمت إعادة تعيين كلمة المرور لـ {staff.username}. الجديدة هي: {new_pass}", "success")
    return redirect(url_for('admin_permissions.roles_list', type=type))

@admin_permissions_bp.route('/admin/permissions/toggle-status/<int:id>/<string:type>', methods=['GET'])
@login_required
def toggle_status(id, type):
    model = AdminStaff if type == 'admin' else SupplierStaff
    staff = model.query.get_or_404(id)
    staff.is_active = not staff.is_active
    db.session.commit()
    status = "نشط" if staff.is_active else "موقوف"
    flash(f"تم تحديث حالة {staff.username} إلى {status}", "info")
    return redirect(url_for('admin_permissions.roles_list', type=type))
