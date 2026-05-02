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
from core.models.user import User # تأكد من مسار نموذج المستخدم لديك

@admin_bp.route('/add_vendor', methods=['POST'])
def add_vendor():
    # 1. استقبال البيانات وتجهيز الحقول اليدوية
    activity = request.form.get('manual_activity') if request.form.get('activity_type') == 'manual' else request.form.get('activity_type')
    id_type = request.form.get('manual_id_type') if request.form.get('id_type') == 'manual' else request.form.get('id_type')
    bank = request.form.get('manual_bank') if request.form.get('bank_name') == 'other' else request.form.get('bank_name')

    try:
        # 2. إنشاء حساب المستخدم أولاً
        new_user = User(username=request.form.get('username'), role='vendor')
        new_user.set_password(request.form.get('password')) # نفترض وجود دالة التشفير
        db.session.add(new_user)
        db.session.flush() # للحصول على user.id قبل الحفظ النهائي

        # 3. إنشاء سجل المورد
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
            e_wallet=request.form.get('e_wallet'), # القادم من الواجهة كـ next_id
            fin_type=request.form.get('fin_type'),
            bank_name=bank,
            bank_acc=request.form.get('bank_acc')
        )
        
        db.session.add(new_vendor)
        db.session.commit()
        
        flash(f"تم تعميد المورد {new_vendor.trade_name} بنجاح", "success")
        return redirect(url_for('admin.add_supplier_page')) # أو صفحة القائمة

    except Exception as e:
        db.session.rollback()
        flash(f"خطأ في النظام: {str(e)}", "danger")
        return redirect(url_for('admin.add_supplier_page'))
