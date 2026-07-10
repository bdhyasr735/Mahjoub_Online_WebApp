# coding: utf-8
# 📂 apps/suppliers_permissions/routes.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff

# تعريف الـ Blueprint لموديول الصلاحيات
suppliers_permissions_bp = Blueprint(
    'suppliers_permissions', 
    __name__, 
    template_folder='templates'
)

def check_supplier_owner_access():
    """تحقق أمني صارم لضمان أن الحساب الحالي هو المورد المالك وليس موظفاً"""
    user_type = session.get('user_type')
    
    # إذا لم يكن المورد المالك الأساسي، ارفض الدخول فوراً
    if user_type != 'supplier':
        return False
        
    # منع الحسابات الإدارية (الـ Admin) من التداخل هنا
    if current_user.__class__.__name__ == 'AdminUser':
        return False
        
    return True

# ✨ تحسين: دعم المسار الرئيسي والفرعي معاً لمنع أي خطأ تتبع برابط القائمة الجانبية
@suppliers_permissions_bp.route('/', methods=['GET', 'POST'])
@suppliers_permissions_bp.route('/permissions', methods=['GET', 'POST'])
@login_required
def permissions():
    """
    عرض وإدارة الموظفين وتعيين الصلاحيات الخاصة بهم من قبل المورد.
    """
    # 1. فحص الحماية والأمان
    if not check_supplier_owner_access():
        flash("عذراً، هذه الصلاحية متاحة فقط لمالك الحساب الأساسي (المورد).", "danger")
        return redirect('/supplier/dashboard')
        
    supplier_id = current_user.id
    supplier = db.session.get(Supplier, supplier_id)
    
    if not supplier:
        flash("لم يكن العثور على بيانات المورد الخاصة بك.", "danger")
        return redirect('/supplier/login')

    # 2. معالجة طلب إضافة موظف جديد (POST)
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        
        # قراءة حالات الـ Switches (الصلاحيات) من النموذج
        can_view_wallet = 'can_view_wallet' in request.form
        can_manage_orders = 'can_manage_orders' in request.form
        can_manage_settings = 'can_manage_settings' in request.form

        # التحقق من المدخلات الأساسية
        if not username or not phone or not password:
            flash("يرجى ملء كافة الحقول الإلزامية واختيار كلمة المرور.", "warning")
        else:
            # الفحص الصارم لمنع تكرار اسم المستخدم أو الهاتف في النظام
            existing_staff = SupplierStaff.query.filter(
                (SupplierStaff.username == username) | 
                (SupplierStaff.search_phone == phone)
            ).first()
            
            if existing_staff:
                flash("تنبيه: اسم المستخدم أو رقم الهاتف هذا مسجل مسبقاً لموظف آخر.", "danger")
            else:
                try:
                    # إنشاء كائن الموظف الجديد وربطه تلقائياً بـ supplier_id الحالي
                    new_staff = SupplierStaff(
                        supplier_id=supplier.id,
                        username=username,
                        search_phone=phone,
                        can_view_wallet=can_view_wallet,
                        can_manage_orders=can_manage_orders,
                        can_manage_settings=can_manage_settings,
                        is_active=True
                    )
                    # تشفير كلمة المرور بأمان
                    new_staff.set_password(password)
                    
                    db.session.add(new_staff)
                    db.session.commit()
                    
                    flash(f"تمت إضافة الموظف ({username}) بنجاح وتعيين صلاحياته المحددة.", "success")
                    return redirect(url_for('suppliers_permissions.permissions'))
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"❌ [Permissions Add Staff Error]: {str(e)}")
                    flash("حدث خطأ داخلي أثناء محاولة حفظ الموظف الجديد.", "danger")

    # 3. جلب قائمة الموظفين الحاليين التابعين لهذا المورد فقط لعرضهم في الجدول
    staff_list = SupplierStaff.query.filter_by(supplier_id=supplier.id).all()
    
    return render_template(
        'suppliers/permissions.html', 
        supplier=supplier, 
        staff_list=staff_list
    )
