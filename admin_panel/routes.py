from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from core.models.user import User
from core import db

# تعريف البلوبرينت - هذا هو السطر الذي كان يسبب الخطأ
# تأكد أن الاسم admin_bp مطابق لما تستدعيه في core/__init__.py
admin_bp = Blueprint('admin_panel', __name__, template_folder='templates')

# --- مسارات الهوية (Authentication) ---

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    # منع الدخول المتكرر إذا كان المستخدم مسجلاً بالفعل كمدير
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin_panel.admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # البحث عن المدير في قاعدة البيانات
        user = User.query.filter_by(username=username, role='admin').first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('مرحباً بك في برج الرقابة.', 'success')
            return redirect(url_for('admin_panel.admin_dashboard'))
        else:
            flash('بيانات الدخول غير صحيحة أو ليس لديك صلاحية الوصول.', 'danger')

    # المسار الفعلي: admin_panel/templates/admin_panel/login.html
    return render_template('admin_panel/login.html')

@admin_bp.route('/logout')
@login_required
def admin_logout():
    logout_user()
    flash('تم تسجيل الخروج من النظام السيادي بنجاح.', 'info')
    return redirect(url_for('admin_panel.admin_login'))

# --- مسارات لوحة التحكم (Dashboard) ---

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    # تأمين المسار: التأكد من أن المستخدم مدير وليس مورداً
    if current_user.role != 'admin':
        return redirect(url_for('supplier_panel.supplier_login'))
        
    return render_template('admin_panel/dashboard.html')

@admin_bp.route('/suppliers-management')
@login_required
def admin_suppliers_management():
    if current_user.role != 'admin':
        return redirect(url_for('admin_panel.admin_login'))
    return render_template('admin_panel/admin_suppliers_management.html')

@admin_bp.route('/wallets')
@login_required
def wallets():
    if current_user.role != 'admin':
        return redirect(url_for('admin_panel.admin_login'))
    return render_template('admin_panel/wallets.html')
