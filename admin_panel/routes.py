from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, logout_user, current_user
from . import admin_bp
from .auth import handle_admin_login
# من المفترض استيراد الموديلات هنا لاحقاً (مثل User, Supplier, Order, WithdrawRequest)

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """معالجة تسجيل دخول السلطة العليا"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    """مركز المراقبة والتحكم المركزي"""
    # هذه البيانات يتم تمريرها للقالب dashboard.html
    stats = {
        'orders_count': "1,250", 
        'suppliers_count': "48",
        'total_balance': "15,500",
        'pending_requests': "12",
        'active_users': "320"
    }
    # تم التعديل لاستدعاء dashboard.html الموجود في مجلد templates الخاص بـ admin_panel
    return render_template('dashboard.html', **stats)

# --- قسم حوكمة الموردين ---

@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_vendor():
    """تعميد مورد جديد في النظام الملكي"""
    if request.method == 'POST':
        # منطق حفظ البيانات وتوليد الرقم السيادي سيضاف هنا
        # "النجاح يبنى بالثقة وليس على الأوراق"
        flash('تم تعميد المورد بنجاح وفتح محافظه المالية الثلاث.', 'success')
        return redirect(url_for('admin.manage_suppliers'))
    
    return render_template('add_supplier.html')

@admin_bp.route('/manage-suppliers')
@login_required
def manage_suppliers():
    """حوكمة الموردين المعتمدين"""
    return render_template('manage_suppliers.html')

# --- قسم الهندسة المالية ---

@admin_bp.route('/withdraw-requests')
@login_required
def withdraw_requests():
    """إدارة طلبات سحب الأرصدة والتسويات"""
    return render_template('withdraw_requests.html')

@admin_bp.route('/financial-engineering')
@login_required
def financial_reports():
    """تقارير الهندسة المالية والأرباح"""
    return render_template('financial_reports.html')

# --- إعدادات السيادة ---

@admin_bp.route('/system-settings')
@login_required
def system_settings():
    """إعدادات السيادة والتحكم بالنظام"""
    return render_template('settings.html')

@admin_bp.route('/logout')
@login_required
def logout():
    """إنهاء الجلسة الآمنة والعودة للشرنقة"""
    logout_user()
    flash('تم إنهاء الجلسة الآمنة بنجاح. ننتظر عودتك يا قائد.', 'info')
    return redirect(url_for('admin.admin_login'))

from flask import render_template, request, redirect, url_for, flash
from . import admin_bp
from core import db
from core.models.vendor import Vendor
from core.models.user import User
from werkzeug.security import generate_password_hash

# البادئة السيادية الثابتة لمحجوب أونلاين
MAH_PREFIX = "MAH-936"

# --- 1. مسار عرض صفحة إضافة مورد ---
@admin_bp.route('/add_supplier')
def add_supplier_page():
    # جلب آخر مورد مسجل للحصول على الرقم التسلسلي التالي من قاعدة البيانات
    last_vendor = Vendor.query.order_by(Vendor.id.desc()).first()
    
    # تحديد الرقم المتغير (ID + 1)
    next_serial = (last_vendor.id + 1) if last_vendor else 1
    
    # دمج البادئة مع الرقم التسلسلي (مثلاً: MAH-9361)
    next_id = f"{MAH_PREFIX}{next_serial}"
    
    return render_template('add_supplier.html', next_id=next_id)

# --- 2. مسار معالجة بيانات التعميد والحفظ ---
@admin_bp.route('/add_vendor_action', methods=['POST'])
def add_vendor_action():
    try:
        # معالجة الحقول التي تدعم الإدخال اليدوي (Activity, ID Type, Bank)
        activity = request.form.get('manual_activity') if request.form.get('activity_type') == 'manual' else request.form.get('activity_type')
        id_type = request.form.get('manual_id_type') if request.form.get('id_type') == 'manual' else request.form.get('id_type')
        bank = request.form.get('manual_bank') if request.form.get('bank_name') == 'other' else request.form.get('bank_name')

        # أ. إنشاء حساب المستخدم (User)
        # نستخدم اسم المستخدم المدخل في النموذج
        username = request.form.get('username')
        password = request.form.get('password')
        
        # التأكد من عدم تكرار اسم المستخدم
        if User.query.filter_by(username=username).first():
            flash("اسم المستخدم موجود مسبقاً، اختر اسماً آخر", "danger")
            return redirect(url_for('admin.add_supplier_page'))

        new_user = User(username=username)
        new_user.set_password(password) # تأكد من وجود الدالة في نموذج User
        db.session.add(new_user)
        db.session.flush() # لحجز ID المستخدم لربطه بالمورد

        # ب. إنشاء سجل المورد (Vendor) بالرقم السيادي الكامل
        # e_wallet تستقبل القيمة المدمجة (البادئة + الرقم) من النموذج
        new_vendor = Vendor(
            user_id=new_user.id,
            owner_name=request.form.get('owner_name'),
            id_type=id_type,
            id_card_number=request.form.get('id_card_number'),
            trade_name=request.form.get('trade_name'),
            activity_type=activity,
            province=request.form.get('province'),
            district=request.form.get('district'),
            address_detail=request.form.get('address_detail'),
            phone=request.form.get('phone'),
            e_wallet=request.form.get('e_wallet'), # القيمة المدمجة مثل MAH-9361
            fin_type=request.form.get('fin_type'),
            bank_name=bank,
            bank_acc=request.form.get('bank_acc'),
            is_verified=True # تعميد سيادي فوري عند الإضافة من الإدارة
        )

        db.session.add(new_vendor)
        db.session.commit()

        flash(f"تم تعميد المورد {new_vendor.trade_name} بنجاح بالرقم: {new_vendor.e_wallet}", "success")
        return redirect(url_for('admin.add_supplier_page'))

    except Exception as e:
        db.session.rollback()
        flash(f"حدث خطأ أثناء عملية التعميد: {str(e)}", "danger")
        return redirect(url_for('admin.add_supplier_page'))
