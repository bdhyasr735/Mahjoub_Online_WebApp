import os
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_required, logout_user
from werkzeug.utils import secure_filename
from core import db 

# استيراد النماذج (Models) - تأكد من مطابقة المسارات في مشروعك
try:
    from core.models import Vendor, User
    # افترضنا وجود هذه النماذج بناءً على طلبك لصفحات السحب والمحافظ
    from core.models.vendor import WithdrawRequest 
except ImportError:
    WithdrawRequest = None
    Vendor = None
    User = None

from . import admin_bp
from .auth import handle_admin_login

# مسار رفع صور الهويات
UPLOAD_FOLDER = 'static/uploads/ids'

# --- 1. بوابة الدخول ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """تستدعي قالب login.html عبر دالة handle_admin_login"""
    return handle_admin_login()

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("تم تأمين الخروج من النظام.", "info")
    return redirect(url_for('admin.login'))

# --- 2. لوحة التحكم الرئيسية ---
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    """تستدعي قالب dashboard.html"""
    suppliers_count = Vendor.query.count() if Vendor else 0
    # يمكنك إضافة إحصائيات أخرى هنا ليتم عرضها في Dashboard
    return render_template('dashboard.html', suppliers_count=suppliers_count)

# --- 3. إدارة الموردين (التعميد) ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """تستدعي قالب add_supplier.html"""
    next_id = 1001
    if Vendor:
        last_vendor = Vendor.query.order_by(Vendor.id.desc()).first()
        if last_vendor:
            next_id = last_vendor.id + 1

    if request.method == 'POST':
        # (نفس منطق الإضافة السابق الذي يحفظ البيانات ويرفع الصورة)
        # ... كود المعالجة ...
        flash(f"تم تعميد المورد بنجاح بالرقم {next_id}", "success")
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('add_supplier.html', next_id=next_id)

# --- 4. طلبات السحب ---
@admin_bp.route('/withdraw-requests')
@login_required
def withdraw_requests():
    """تستدعي قالب withdraw_requests.html"""
    # جلب الطلبات المعلقة فقط
    requests_list = WithdrawRequest.query.filter_by(status='pending').all() if WithdrawRequest else []
    return render_template('withdraw_requests.html', requests=requests_list)

# --- 5. إدارة المحافظ السيادية ---
@admin_bp.route('/wallets')
@login_required
def wallets():
    """تستدعي قالب wallets.html"""
    # عرض قائمة الموردين مع أرصدتهم (المحافظ الرقمية)
    all_vendors = Vendor.query.all() if Vendor else []
    return render_template('wallets.html', vendors=all_vendors)
