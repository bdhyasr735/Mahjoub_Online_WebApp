from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from core.models.user import User
from core.extensions import db
import json

# تعريف البلوبرنت الخاص بالطاقم تحت المسار السيادي /admin/staff
staff_bp = Blueprint('staff', __name__, url_prefix='/admin/staff')

@staff_bp.route('/manage')
@login_required
def manage_staff():
    # التحقق من الصلاحية: القائد فقط (علي محجوب) أو الـ super_admin يمكنه رؤية الطاقم
    if current_user.role not in ['admin', 'super_admin']:
        flash('ليس لديك صلاحية الوصول إلى سجلات الطاقم السيادية.', 'danger')
        return redirect(url_for('admin.dashboard'))

    # جلب فريق الإدارة (الذين لا يتبعون مورد معين لضمان استقلالية الإدارة العليا)
    admin_team = User.query.filter(User.supplier_id == None, User.role != 'super_admin').all()
    
    # التوجيه للمسار الجديد داخل مجلد staff
    return render_template('staff/manage_staff.html', admin_team=admin_team)

@staff_bp.route('/add', methods=['POST'])
@login_required
def add_staff_member():
    # حماية المسار: منع أي شخص غير القائد من إضافة موظفين
    if current_user.role not in ['admin', 'super_admin']:
        flash('صلاحية سيادية مطلوبة لتعميد أفراد جدد!', 'danger')
        return redirect(url_for('staff.manage_staff'))

    # استلام البيانات من النموذج المؤمن بـ CSRF
    username = request.form.get('username')
    password = request.form.get('password')
    full_name = request.form.get('full_name')
    role = request.form.get('role')
    
    # بروتوكول تجميع الصلاحيات الرقمية (Governance JSON)
    perms = {
        "can_manage_suppliers": 'manage_suppliers' in request.form,
        "can_approve_products": 'approve_products' in request.form,
        "can_view_finance": 'view_finance' in request.form
    }

    # التحقق من عدم تكرار الهوية الرقمية (Username)
    if User.query.filter_by(username=username).first():
        flash('هذا المستخدم مسجل مسبقاً في الترسانة!', 'warning')
        return redirect(url_for('staff.manage_staff'))

    try:
        # إنشاء الموظف الجديد (لاحظ استخدام json.dumps لتخزين الصلاحيات كـ TEXT)
        new_member = User(
            username=username,
            full_name=full_name,
            role=role,
            permissions=json.dumps(perms)
        )
        
        # تشفير كلمة المرور فوراً (بروتوكول الأمان)
        new_member.set_password(password)
        
        db.session.add(new_member)
        db.session.commit()
        
        flash(f'تم تعميد الموظف {full_name} بنجاح ضمن طاقم القيادة.', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'حدث عطل تقني أثناء التعميد: {str(e)}', 'danger')

    return redirect(url_for('staff.manage_staff'))
