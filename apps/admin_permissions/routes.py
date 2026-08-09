from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models import AdminStaff, Supplier  # استبدل النماذج حسب هيكلة مشروعك الفعلية
from apps.admin_permissions.registry import ADMIN_PERMISSIONS_REGISTRY, SUPPLIER_PERMISSIONS_REGISTRY

admin_permissions_bp = Blueprint('admin_permissions', __name__, template_folder='templates')

@admin_permissions_bp.route('/', methods=['GET'])
@login_required
def index():
    """عرض قائمة الموظفين وإحصائيات لوحة الصلاحيات"""
    page = request.args.get('page', 1, type=int)
    staff_type = request.args.get('staff_type', 'admin_staff')
    
    user_scope = 'admin' if getattr(current_user, 'is_admin', True) else 'supplier'
    can_manage = True

    # جلب البيانات مع ترقيم الصفحات
    if staff_type == 'admin_staff':
        pagination = AdminStaff.query.order_by(AdminStaff.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
        staff_list = pagination.items
        perm_dict = ADMIN_PERMISSIONS_REGISTRY
    else:
        # افتراضي لموظفي الموردين (يمكنك تعديل نموذج الاستعلام حسب جدولك)
        pagination = AdminStaff.query.paginate(page=page, per_page=10, error_out=False) # استبدلها بنموذج SupplierStaff
        staff_list = []
        perm_dict = SUPPLIER_PERMISSIONS_REGISTRY

    # إحصائيات البطاقات
    admin_staffs = AdminStaff.query.all()
    suppliers = Supplier.query.all() if hasattr(Supplier, 'query') else []
    supplier_staffs = [] # استبدل استعلام موظفي الموردين هنا

    return render_template(
        'admin/permissions.html',
        user_scope=user_scope,
        can_manage=can_manage,
        staff_list=staff_list,
        staff_type=staff_type,
        pagination=pagination,
        admin_staffs=admin_staffs,
        suppliers=suppliers,
        supplier_staffs=supplier_staffs,
        perm_dict=perm_dict,
        admin_permissions_list=ADMIN_PERMISSIONS_REGISTRY,
        supplier_permissions_list=SUPPLIER_PERMISSIONS_REGISTRY,
        brand_color='#4A154B'
    )

@admin_permissions_bp.route('/staff/add', methods=['POST'])
@login_required
def add_staff():
    """إضافة موظف جديد مع التحقق التام من البيانات الأساسية"""
    try:
        staff_type = request.form.get('staff_type', 'admin_staff')
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip() or None
        role_title = request.form.get('role_title', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not name or not password:
            return jsonify({'status': 'error', 'message': 'يرجى تعبئة الحقول الأساسية الإجبارية (الاسم، اسم المستخدم، كلمة المرور).'}), 400

        # التحقق اللحظي من عدم التكرار قبل الحفظ منعاً للتعارض
        if AdminStaff.query.filter_by(username=username).first():
            return jsonify({'status': 'error', 'message': 'اسم المستخدم مستخدم مسبقاً.'}), 400
        if email and AdminStaff.query.filter_by(email=email).first():
            return jsonify({'status': 'error', 'message': 'البريد الإلكتروني مستخدم مسبقاً.'}), 400
        if phone and AdminStaff.query.filter_by(phone=phone).first():
            return jsonify({'status': 'error', 'message': 'رقم الهاتف مستخدم مسبقاً.'}), 400

        if staff_type == 'admin_staff':
            perms = {}
            for key in request.form:
                if key.startswith('perm_'):
                    perms[key.replace('perm_', '')] = True

            new_staff = AdminStaff(
                name=name,
                username=username,
                phone=phone,
                email=email,
                role_title=role_title or 'موظف إداري',
                is_active=True,
                permissions=perms
            )
            new_staff.set_password(password)
            db.session.add(new_staff)
            db.session.commit()

        elif staff_type == 'supplier_staff':
            supplier_id = request.form.get('supplier_id')
            if not supplier_id:
                return jsonify({'status': 'error', 'message': 'يرجى اختيار المورد التابع له الموظف.'}), 400
            
            # حفظ موظف المورد في الجدول الخاص به هنا
            pass

        return jsonify({
            'status': 'success',
            'message': f'تم إضافة الموظف ({name}) بنجاح وتعيين صلاحياته.'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'حدث خطأ غير متوقع: {str(e)}'}), 500

@admin_permissions_bp.route('/check-availability', methods=['GET'])
@login_required
def check_availability():
    """مسار الاستعلام اللحظي للتأكد من عدم تكرار البيانات (الهاتف، البريد، اسم المستخدم)"""
    field = request.args.get('field')
    value = request.args.get('value')
    
    exists = False
    if field == 'username':
        exists = AdminStaff.query.filter_by(username=value).first() is not None
    elif field == 'email':
        exists = AdminStaff.query.filter_by(email=value).first() is not None
    elif field == 'phone':
        exists = AdminStaff.query.filter_by(phone=value).first() is not None
        
    return jsonify({'exists': exists})

@admin_permissions_bp.route('/staff/<int:target_id>/update-permissions', methods=['POST'])
@login_required
def update_permissions(target_id):
    """تعديل صلاحيات موظف معين"""
    try:
        staff = AdminStaff.query.get_or_404(target_id)
        perms = {}
        for key in request.form:
            if key.startswith('perm_'):
                perms[key.replace('perm_', '')] = True
        
        staff.permissions = perms
        db.session.commit()
        flash('تم تحديث صلاحيات الموظف بنجاح.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء التحديث: {str(e)}', 'danger')
        
    return redirect(url_for('admin_permissions.index'))
