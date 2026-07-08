# coding: utf-8
# 📂 apps/admin_permissions/routes.py

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
import secrets
import string

from apps.extensions import db
# تم تعديل المسار هنا ليطابق اسم الملف الفعلي لديك
from apps.models.admin_staff_db import AdminStaff 

# تعريف الـ Blueprint
admin_permissions_bp = Blueprint(
    'admin_permissions', 
    __name__, 
    template_folder='templates'
)

# دالة التحقق من الصلاحيات السيادية
def is_admin():
    return current_user.is_authenticated and (getattr(current_user, 'role', '') in ['admin', 'Owner'])

# دالة توليد كلمة مرور عشوائية قوية
def generate_random_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

@admin_permissions_bp.route('/admin/permissions/roles', methods=['GET'])
@login_required
def roles_list():
    """عرض قائمة الموظفين مع خاصية البحث والترقيم الصفحي."""
    if not is_admin():
        flash("غير مصرح لك.", "danger")
        return redirect(url_for('admin_dashboard.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    
    query = AdminStaff.query
    if search:
        query = query.filter(AdminStaff.username.contains(search) | AdminStaff.email.contains(search))
        
    pagination = query.paginate(page=page, per_page=10)
    return render_template('admin/permissions.html', 
                           staff=pagination.items, 
                           pagination=pagination, 
                           active_tab='roles')

@admin_permissions_bp.route('/admin/permissions/assign', methods=['POST'])
@login_required
def assign_permissions():
    """إضافة موظف جديد عبر النافذة المنبثقة."""
    if not is_admin(): return redirect(url_for('admin_dashboard.dashboard'))
    
    username = request.form.get('username')
    email = request.form.get('email')
    
    if username and email:
        new_staff = AdminStaff(username=username, email=email, role='worker', is_active=True)
        new_staff.set_password('123456') # كلمة مرور افتراضية أولية
        db.session.add(new_staff)
        db.session.commit()
        flash(f"تمت إضافة الموظف {username} بنجاح", "success")
    else:
        flash("بيانات غير مكتملة", "danger")
        
    return redirect(url_for('admin_permissions.roles_list'))

@admin_permissions_bp.route('/admin/permissions/reset-password/<int:id>', methods=['GET'])
@login_required
def reset_password(id):
    """إعادة تعيين كلمة المرور وتوليدها عشوائياً."""
    staff = AdminStaff.query.get_or_404(id)
    new_pass = generate_random_password()
    staff.set_password(new_pass)
    db.session.commit()
    flash(f"تمت إعادة تعيين كلمة المرور لـ {staff.username}. الجديدة هي: {new_pass}", "success")
    return redirect(url_for('admin_permissions.roles_list'))

@admin_permissions_bp.route('/admin/permissions/toggle-status/<int:id>', methods=['GET'])
@login_required
def toggle_status(id):
    """تفعيل أو إيقاف حساب الموظف."""
    staff = AdminStaff.query.get_or_404(id)
    staff.is_active = not staff.is_active
    db.session.commit()
    status = "نشط" if staff.is_active else "موقوف"
    flash(f"تم تحديث حالة {staff.username} إلى {status}", "info")
    return redirect(url_for('admin_permissions.roles_list'))
