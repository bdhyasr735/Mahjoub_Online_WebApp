# -*- coding: utf-8 -*-
import json
from functools import wraps
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user

# استيراد النماذج وقاعدة البيانات من الموديول الرئيسي للنظام
from apps.models import db, AdminUser, AdminStaff, Supplier, SupplierStaff

permissions_bp = Blueprint(
    'admin_permissions',
    __name__,
    template_folder='templates'
)

# ==========================================
# قائمة الصلاحيات القياسية لنظام محجوب أونلاين
# ==========================================
ADMIN_PERMISSIONS_LIST = {
    'manage_staff': 'إدارة موظفي الإدارة والصلاحيات',
    'manage_suppliers': 'إدارة الموردين وتفعيل حساباتهم',
    'manage_products': 'إدارة المنتجات والأقسام',
    'manage_orders': 'إدارة وسحب الطلبات والعمليات',
    'view_financials': 'الاطلاع على التقارير المالية والتقارير العامة',
    'manage_settings': 'تعديل إعدادات المنصة والهوية'
}

SUPPLIER_PERMISSIONS_LIST = {
    'manage_catalog': 'إضافة وتحديث المنتجات والمخزون',
    'process_orders': 'معالجة وتجهيز طلبات الشراء',
    'view_supplier_reports': 'عرض التقارير المبيعات الخاصة بالمورد',
    'manage_substaff': 'إدارة موظفي المورد الفرعيين'
}


# ==========================================
# الديكورات المخصصة للحماية والتحكم بالوصول
# ==========================================
def require_super_admin(f):
    """زخرفة تسمح بالدخول فقط للإدارة العليا (AdminUser)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, AdminUser):
            flash("عفواً، هذه الصفحة مخصصة لمالكي النظام والمدراء التنفيذيين فقط.", "danger")
            return redirect(url_for('admin_permissions.index'))
        return f(*args, **kwargs)
    return decorated_function


def can_manage_permissions(user):
    """دالة فحص هل للـ User صلاحية التعديل على الصلاحيات"""
    if isinstance(user, AdminUser):
        return True
    if isinstance(user, AdminStaff):
        perms = getattr(user, 'permissions', {}) or {}
        if isinstance(perms, str):
            try: perms = json.loads(perms)
            except: perms = {}
        return perms.get('manage_staff', False)
    if isinstance(user, Supplier):
        return True # المورد له صلاحية إدارة موظفيه
    return False


# ==========================================
# المسارات والوظائف البرمجية
# ==========================================

@permissions_bp.route('/', methods=['GET'])
@login_required
def index():
    """
    عرض شاشة التحكم بالصلاحيات والموظفين والموردين
    """
    # فحص نوع المستخدم وسحب الموظفين المناسبين لنطاق الصلاحيات
    if isinstance(current_user, (AdminUser, AdminStaff)):
        admin_staffs = AdminStaff.query.all()
        suppliers = Supplier.query.all()
        supplier_staffs = SupplierStaff.query.all()
        user_scope = 'admin'
    elif isinstance(current_user, Supplier):
        admin_staffs = []
        suppliers = [current_user]
        supplier_staffs = SupplierStaff.query.filter_by(supplier_id=current_user.id).all()
        user_scope = 'supplier'
    else:
        flash("غير مسموح لك بالوصول لصفحة إدارة الصلاحيات.", "warning")
        return redirect('/')

    return render_template(
        'admin_permissions/permissions.html',
        admin_staffs=admin_staffs,
        suppliers=suppliers,
        supplier_staffs=supplier_staffs,
        admin_permissions_list=ADMIN_PERMISSIONS_LIST,
        supplier_permissions_list=SUPPLIER_PERMISSIONS_LIST,
        user_scope=user_scope,
        can_manage=can_manage_permissions(current_user)
    )


@permissions_bp.route('/update-user-permissions/<string:target_type>/<int:target_id>', methods=['POST'])
@login_required
def update_permissions(target_type, target_id):
    """
    مسار تحديث وحفظ الصلاحيات الخاصة بالموظف أو المورد
    """
    if not can_manage_permissions(current_user):
        return jsonify({'status': 'error', 'message': 'لا تملك الصلاحية الكافية لتعديل الأذونات.'}), 403

    # استخراج البيانات المرسلة (JSON أو Form Data)
    if request.is_json:
        data = request.get_json()
        selected_permissions = data.get('permissions', {})
    else:
        # من خلال إرسال Form عادي
        selected_permissions = {}
        prefix = 'perm_'
        for key, value in request.form.items():
            if key.startswith(prefix):
                perm_name = key[len(prefix):]
                selected_permissions[perm_name] = True if value == 'on' else False

    target_user = None

    try:
        # 1. موظف إدارة
        if target_type == 'admin_staff':
            if not isinstance(current_user, (AdminUser, AdminStaff)):
                return jsonify({'status': 'error', 'message': 'غير مصرح لك بتعديل أذونات كادر الإدارة.'}), 403
            target_user = AdminStaff.query.get_or_404(target_id)
            target_user.permissions = selected_permissions

        # 2. موظف مورد
        elif target_type == 'supplier_staff':
            target_user = SupplierStaff.query.get_or_404(target_id)
            # التأكد أن المورد يشرف على الموظف الخاضع للتعديل
            if isinstance(current_user, Supplier) and target_user.supplier_id != current_user.id:
                return jsonify({'status': 'error', 'message': 'لا يمكنك تعديل موظفي موردين آخرين.'}), 403
            target_user.permissions = selected_permissions

        else:
            return jsonify({'status': 'error', 'message': 'نوع المستهدف غير معروف.'}), 400

        db.session.commit()
        
        if request.is_json:
            return jsonify({'status': 'success', 'message': f'تم تحديث صلاحيات {getattr(target_user, "name", "المستخدم")} بنجاح.'})
        
        flash(f'تم تحديث الصلاحيات بنجاح لـ {getattr(target_user, "name", "المستخدم")}.', 'success')
        return redirect(url_for('admin_permissions.index'))

    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'status': 'error', 'message': f'حدث خطأ أثناء الحفظ: {str(e)}'}), 500
        flash('حدث خطأ أثناء التحديث.', 'danger')
        return redirect(url_for('admin_permissions.index'))


@permissions_bp.route('/toggle-status/<string:target_type>/<int:target_id>', methods=['POST'])
@login_required
def toggle_status(target_type, target_id):
    """
    تفعيل أو إيقاف حساب موظف/مورد سريعاً
    """
    if not can_manage_permissions(current_user):
        return jsonify({'status': 'error', 'message': 'إجراء غير مصرح به.'}), 403

    model_map = {
        'admin_staff': AdminStaff,
        'supplier': Supplier,
        'supplier_staff': SupplierStaff
    }

    model = model_map.get(target_type)
    if not model:
        return jsonify({'status': 'error', 'message': 'النوع المفضل غير صالح.'}), 400

    user_obj = model.query.get_or_404(target_id)
    
    # حماية: المورد لا يوقف سوى موظفيه
    if isinstance(current_user, Supplier) and target_type == 'supplier_staff' and user_obj.supplier_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'غير متاح.'}), 403

    if hasattr(user_obj, 'is_active'):
        user_obj.is_active = not user_obj.is_active
        db.session.commit()
        status_txt = "نشط" if user_obj.is_active else "معطل"
        return jsonify({'status': 'success', 'message': f'تم تغيير حالة الحساب إلى ({status_txt}).', 'is_active': user_obj.is_active})

    return jsonify({'status': 'error', 'message': 'هذا الحساب لا يدعم التغيير السريع للوضع.'}), 400