# -*- coding: utf-8 -*-
import json
from functools import wraps
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user

# استيراد قاعدة البيانات والنماذج 
from apps.models import db, AdminUser, AdminStaff, Supplier, SupplierStaff

admin_permissions_bp = Blueprint(
    'admin_permissions',
    __name__,
    url_prefix='/admin/permissions',
    template_folder='templates'
)

# ==========================================
# مصفوفة الصلاحيات القياسية لمنصة محجوب أونلاين
# ==========================================
ADMIN_PERMISSIONS = {
    'manage_staff': 'إدارة موظفي الإدارة والصلاحيات',
    'manage_suppliers': 'إدارة حسابات الموردين',
    'manage_products': 'إدارة المنتجات والأقسام',
    'manage_orders': 'معالجة وتتبع الطلبات',
    'view_reports': 'عرض التقارير المالية والإحصائيات',
    'manage_settings': 'تعديل إعدادات النظام'
}

SUPPLIER_PERMISSIONS = {
    'manage_catalog': 'إضافة وتعديل منتجات المورد',
    'process_orders': 'معالجة طلبات الشراء الواردة',
    'view_supplier_reports': 'عرض تقارير مبيعات المورد',
    'manage_substaff': 'إدارة موظفي المورد الفرعيين'
}

# ==========================================
# التحقق ودوال المساعدة (Helpers & Decorators)
# ==========================================
def check_permission_access(user):
    """فحص إمكانية المستخدم للوصول والتعديل في شاشة الصلاحيات"""
    if isinstance(user, AdminUser):
        return True
    if isinstance(user, AdminStaff):
        perms = getattr(user, 'permissions', {}) or {}
        if isinstance(perms, str):
            try: perms = json.loads(perms)
            except: perms = {}
        return perms.get('manage_staff', False)
    if isinstance(user, Supplier):
        return True # المورد يملك صلاحية كاملة على موظفيه
    return False

# ==========================================
# المسارات (Routes)
# ==========================================

@admin_permissions_bp.route('/', methods=['GET'])
@login_required
def index():
    """عرض الشاشة الرئيسية لإدارة الصلاحيات مع دعم Pagination"""
    if not check_permission_access(current_user) and not isinstance(current_user, (AdminUser, AdminStaff, Supplier)):
        flash("غير مسموح لك بالوصول لإدارة الصلاحيات.", "danger")
        return redirect('/')

    # استقبال رقم الصفحة الحالية من الـ Request (الافتراضي هي الصفحة الأولى)
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # جلب قائمة الموردين بشكل دائم لتعبئة خانة المتاجر في واجهة الإضافة
    all_suppliers = Supplier.query.all()

    # تحديد النطاق والمستخدمين بناءً على رتبة الحساب الحالي مع تطبيق الـ Pagination
    if isinstance(current_user, (AdminUser, AdminStaff)):
        admin_pagination = AdminStaff.query.paginate(page=page, per_page=per_page, error_out=False)
        admin_staffs = admin_pagination.items
        
        supplier_pagination = SupplierStaff.query.paginate(page=page, per_page=per_page, error_out=False)
        supplier_staffs = supplier_pagination.items
        
        user_scope = 'admin'
        
    elif isinstance(current_user, Supplier):
        admin_staffs = []
        
        supplier_pagination = SupplierStaff.query.filter_by(supplier_id=current_user.id).paginate(page=page, per_page=per_page, error_out=False)
        supplier_staffs = supplier_pagination.items
        
        user_scope = 'supplier'
    else:
        admin_staffs, supplier_staffs = [], []
        user_scope = 'restricted'
        supplier_pagination = None
        admin_pagination = None

    return render_template(
        'admin/permissions.html',
        admin_staffs=admin_staffs,
        suppliers=all_suppliers,  # تمرير قائمة الموردين المتاحة بالكامل للقالب
        supplier_staffs=supplier_staffs,
        # تمرير كائنات الـ pagination للقوالب
        pagination=supplier_pagination if user_scope == 'supplier' else admin_pagination,
        admin_permissions_list=ADMIN_PERMISSIONS,
        supplier_permissions_list=SUPPLIER_PERMISSIONS,
        user_scope=user_scope,
        can_manage=check_permission_access(current_user)
    )


@admin_permissions_bp.route('/add-staff', methods=['POST'])
@login_required
def add_staff():
    """إضافة موظف جديد (إدارة أو مورد) مع تحديد صلاحياته أولياً وتلقي اسم المستخدم ورقم الهاتف"""
    if not check_permission_access(current_user):
        return jsonify({'status': 'error', 'message': 'غير مصرح لك بإضافة موظفين جُدد.'}), 403

    try:
        staff_type = request.form.get('staff_type')
        name = request.form.get('name')
        username = request.form.get('username')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        role_title = request.form.get('role_title', 'موظف')

        if not name or not username or not email or not password:
            return jsonify({'status': 'error', 'message': 'يرجى ملء جميع الحقول الإلزامية (الاسم، اسم المستخدم، البريد، وكلمة المرور).'}), 400

        # استخراج الصلاحيات المحددة من النموذج
        selected_permissions = {}
        prefix = 'perm_'
        for key, val in request.form.items():
            if key.startswith(prefix):
                perm_key = key[len(prefix):]
                selected_permissions[perm_key] = True

        if staff_type == 'admin_staff' and isinstance(current_user, (AdminUser, AdminStaff)):
            # التحقق من عدم تكرار البريد أو اسم المستخدم أو الهاتف لموظفي الإدارة
            if AdminStaff.query.filter((AdminStaff.email == email) | (AdminStaff.username == username) | ((AdminStaff.phone == phone) if phone else False)).first():
                return jsonify({'status': 'error', 'message': 'البريد الإلكتروني أو اسم المستخدم أو رقم الهاتف مستخدم بالفعل.'}), 400
            
            new_staff = AdminStaff(
                name=name,
                username=username,
                phone=phone,
                email=email,
                role_title=role_title,
                permissions=selected_permissions,
                is_active=True
            )
            new_staff.set_password(password)
            db.session.add(new_staff)

        elif staff_type == 'supplier_staff':
            supplier_id = request.form.get('supplier_id')
            if isinstance(current_user, Supplier):
                supplier_id = current_user.id

            if not supplier_id:
                return jsonify({'status': 'error', 'message': 'يجب تحديد المورد التابع له الموظف.'}), 400

            # التحقق من عدم تكرار البيانات لموظفي الموردين
            if SupplierStaff.query.filter((SupplierStaff.email == email) | (SupplierStaff.username == username) | ((SupplierStaff.phone == phone) if phone else False)).first():
                return jsonify({'status': 'error', 'message': 'البريد الإلكتروني أو اسم المستخدم أو رقم الهاتف مستخدم بالفعل.'}), 400

            new_staff = SupplierStaff(
                supplier_id=supplier_id,
                name=name,
                username=username,
                phone=phone,
                email=email,
                role_title=role_title,
                permissions=selected_permissions,
                is_active=True
            )
            new_staff.set_password(password)
            db.session.add(new_staff)
        else:
            return jsonify({'status': 'error', 'message': 'نوع الموظف غير صالح.'}), 400

        db.session.commit()
        return jsonify({'status': 'success', 'message': f'تمت إضافة الموظف ({name}) بنجاح.'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'حدث خطأ أثناء الإضافة: {str(e)}'}), 500


@admin_permissions_bp.route('/update/<string:target_type>/<int:target_id>', methods=['POST'])
@login_required
def update_permissions(target_type, target_id):
    """تعديل وحفظ أذونات الموظف"""
    if not check_permission_access(current_user):
        return jsonify({'status': 'error', 'message': 'لا تملك صلاحية تعديل الأذونات.'}), 403

    try:
        if request.is_json:
            data = request.get_json()
            selected_permissions = data.get('permissions', {})
        else:
            selected_permissions = {}
            prefix = 'perm_'
            for key, val in request.form.items():
                if key.startswith(prefix):
                    selected_permissions[key[len(prefix):]] = True

        if target_type == 'admin_staff':
            if not isinstance(current_user, (AdminUser, AdminStaff)):
                return jsonify({'status': 'error', 'message': 'غير مصرح.'}), 403
            user_obj = AdminStaff.query.get_or_404(target_id)
        elif target_type == 'supplier_staff':
            user_obj = SupplierStaff.query.get_or_404(target_id)
            if isinstance(current_user, Supplier) and user_obj.supplier_id != current_user.id:
                return jsonify({'status': 'error', 'message': 'غير مسموح لك بتعديل موظف كادر آخر.'}), 403
        else:
            return jsonify({'status': 'error', 'message': 'نوع الحساب غير معروف.'}), 400

        user_obj.permissions = selected_permissions
        db.session.commit()

        if request.is_json:
            return jsonify({'status': 'success', 'message': 'تم تحديث الصلاحيات بنجاح.'})
        
        flash('تم حفظ الصلاحيات بنجاح.', 'success')
        return redirect(url_for('admin_permissions.index'))

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'خطأ أثناء التحديث: {str(e)}'}), 500


@admin_permissions_bp.route('/toggle-status/<string:target_type>/<int:target_id>', methods=['POST'])
@login_required
def toggle_status(target_type, target_id):
    """تنشيط أو إيقاف حساب موظف"""
    if not check_permission_access(current_user):
        return jsonify({'status': 'error', 'message': 'إجراء غير مسموح به.'}), 403

    model_map = {
        'admin_staff': AdminStaff,
        'supplier': Supplier,
        'supplier_staff': SupplierStaff
    }

    model = model_map.get(target_type)
    if not model:
        return jsonify({'status': 'error', 'message': 'نوع الفئة غير صالح.'}), 400

    user_obj = model.query.get_or_404(target_id)
    
    if isinstance(current_user, Supplier) and target_type == 'supplier_staff' and user_obj.supplier_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'غير مصرح.'}), 403

    if hasattr(user_obj, 'is_active'):
        user_obj.is_active = not user_obj.is_active
        db.session.commit()
        status_str = "نشط" if user_obj.is_active else "معطل"
        return jsonify({'status': 'success', 'message': f'تم تغيير حالة الحساب إلى ({status_str}).', 'is_active': user_obj.is_active})

    return jsonify({'status': 'error', 'message': 'الحساب لا يدعم هذه الخاصية.'}), 400