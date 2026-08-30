# apps/admin_permissions/routes.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.admin_db import AdminUser
from apps.models.admin_staff_db import AdminStaff
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.supplier_db import Supplier

# إنشاء Blueprint
admin_permissions_bp = Blueprint(
    'admin_permissions',
    __name__,
    template_folder='templates',
    url_prefix='/admin/permissions'
)


@admin_permissions_bp.route('/')
@login_required
def index():
    """الصفحة الرئيسية لإدارة الصلاحيات"""
    
    # التحقق من صلاحية المستخدم (فقط الإداريين)
    if not isinstance(current_user, (AdminUser, AdminStaff)):
        flash("غير مصرح لك بالوصول إلى هذه الصفحة.", "danger")
        return redirect(url_for('admin_dashboard.index'))
    
    # جلب بيانات الموظفين
    admin_staffs = AdminStaff.query.filter_by(is_active=True).all()
    supplier_staffs = SupplierStaff.query.filter_by(is_active=True).all()
    
    # تحديد نطاق المستخدم
    user_scope = 'admin' if isinstance(current_user, AdminUser) else 'supplier'
    can_manage = True  # يمكن تعديلها حسب الصلاحيات
    
    # قائمة الصلاحيات
    admin_permissions_list = {
        'manage_staff': 'إدارة الموظفين',
        'manage_suppliers': 'إدارة الموردين',
        'manage_products': 'إدارة المنتجات',
        'manage_orders': 'إدارة الطلبات',
        'view_reports': 'عرض التقارير',
        'manage_finance': 'إدارة المالية',
        'manage_settings': 'إدارة الإعدادات'
    }
    
    supplier_permissions_list = {
        'manage_products': 'إدارة المنتجات',
        'manage_orders': 'إدارة الطلبات',
        'view_reports': 'عرض التقارير',
        'manage_staff': 'إدارة الموظفين',
        'manage_finance': 'إدارة المالية'
    }
    
    return render_template(
        'admin/permissions.html',
        page_title='إدارة الصلاحيات',
        admin_staffs=admin_staffs,
        supplier_staffs=supplier_staffs,
        user_scope=user_scope,
        can_manage=can_manage,
        admin_permissions_list=admin_permissions_list,
        supplier_permissions_list=supplier_permissions_list
    )


@admin_permissions_bp.route('/toggle-status/<string:user_type>/<int:user_id>', methods=['POST'])
@login_required
def toggle_status(user_type, user_id):
    """تبديل حالة الموظف (نشط/معطل)"""
    
    # التحقق من الصلاحية
    if not isinstance(current_user, (AdminUser, AdminStaff)):
        return jsonify({'status': 'error', 'message': 'غير مصرح لك بهذا الإجراء.'}), 403
    
    try:
        if user_type == 'admin_staff':
            user = AdminStaff.query.get(user_id)
        elif user_type == 'supplier_staff':
            user = SupplierStaff.query.get(user_id)
        else:
            return jsonify({'status': 'error', 'message': 'نوع المستخدم غير صحيح.'}), 400
        
        if not user:
            return jsonify({'status': 'error', 'message': 'المستخدم غير موجود.'}), 404
        
        # تبديل الحالة
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'تم {"تفعيل" if user.is_active else "تعطيل"} المستخدم بنجاح.',
            'is_active': user.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_permissions_bp.route('/update-permissions/<string:user_type>/<int:user_id>', methods=['POST'])
@login_required
def update_permissions(user_type, user_id):
    """تحديث صلاحيات الموظف"""
    
    if not isinstance(current_user, (AdminUser, AdminStaff)):
        return jsonify({'status': 'error', 'message': 'غير مصرح لك بهذا الإجراء.'}), 403
    
    try:
        data = request.get_json()
        permissions = data.get('permissions', {})
        
        if user_type == 'admin_staff':
            user = AdminStaff.query.get(user_id)
        elif user_type == 'supplier_staff':
            user = SupplierStaff.query.get(user_id)
        else:
            return jsonify({'status': 'error', 'message': 'نوع المستخدم غير صحيح.'}), 400
        
        if not user:
            return jsonify({'status': 'error', 'message': 'المستخدم غير موجود.'}), 404
        
        # تحديث الصلاحيات
        user.permissions = permissions
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'تم تحديث الصلاحيات بنجاح.',
            'permissions': permissions
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_permissions_bp.route('/add-staff', methods=['POST'])
@login_required
def add_staff():
    """إضافة موظف جديد"""
    
    if not isinstance(current_user, (AdminUser, AdminStaff)):
        flash("غير مصرح لك بهذا الإجراء.", "danger")
        return redirect(url_for('admin_permissions.index'))
    
    try:
        data = request.form
        user_type = data.get('user_type', 'admin_staff')
        
        if user_type == 'admin_staff':
            new_staff = AdminStaff(
                username=data.get('username'),
                name=data.get('name'),
                email=data.get('email'),
                role_title=data.get('role_title', 'موظف'),
                is_active=True,
                permissions={}
            )
        else:
            # مورد معين
            supplier_id = data.get('supplier_id')
            if not supplier_id:
                flash("يرجى تحديد المورد.", "danger")
                return redirect(url_for('admin_permissions.index'))
            
            new_staff = SupplierStaff(
                supplier_id=supplier_id,
                full_name=data.get('name'),
                email=data.get('email'),
                username=data.get('username'),
                phone=data.get('phone', ''),
                is_active=True,
                permissions={}
            )
        
        new_staff.set_password(data.get('password', '123456'))
        db.session.add(new_staff)
        db.session.commit()
        
        flash("تم إضافة الموظف بنجاح.", "success")
        return redirect(url_for('admin_permissions.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f"خطأ في إضافة الموظف: {str(e)}", "danger")
        return redirect(url_for('admin_permissions.index'))
