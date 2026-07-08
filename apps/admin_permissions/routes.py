# coding: utf-8
# 📂 apps/admin_permissions/routes.py

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

# استيراد الموارد المطلوبة من المصادر المركزية
from apps.extensions import db
from apps.models import AdminStaff 

# تعريف الـ Blueprint مع تحديد مسار القوالب
admin_permissions_bp = Blueprint(
    'admin_permissions', 
    __name__, 
    template_folder='templates'
)

# دالة مساعدة للتحقق من الصلاحيات السيادية
def is_admin():
    """التحقق من أن المستخدم مسجل وله صلاحية الإدارة (admin أو Owner)."""
    return current_user.is_authenticated and (getattr(current_user, 'role', '') in ['admin', 'Owner'])

@admin_permissions_bp.route('/admin/permissions/roles', methods=['GET'])
@login_required
def roles_list():
    """عرض قائمة الموظفين الإداريين وأدوارهم الحالية في النظام."""
    if not is_admin():
        flash("عذراً، غير مصرح لك بالدخول إلى هذه الصفحة.", "danger")
        return redirect(url_for('admin_dashboard.dashboard'))
    
    # جلب جميع الموظفين الإداريين لعرض أدوارهم من جدول AdminStaff
    staff_members = AdminStaff.query.all()
    
    return render_template(
        'admin/permissions.html', 
        staff=staff_members, 
        active_tab='roles'
    )

@admin_permissions_bp.route('/admin/permissions/assign', methods=['GET', 'POST'])
@login_required
def assign_permissions():
    """صفحة إسناد الصلاحيات للمستخدمين."""
    if not is_admin():
        flash("عذراً، غير مصرح لك بالدخول إلى هذه الصفحة.", "danger")
        return redirect(url_for('admin_dashboard.dashboard'))
    
    # منطق الإسناد سيتم بناؤه هنا لاحقاً بناءً على هيكلية الـ AdminStaff
    return render_template('admin/permissions.html', active_tab='assign')
