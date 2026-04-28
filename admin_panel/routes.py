from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app
from flask_login import login_user, logout_user, login_required, current_user
from core import db
from core.models.user import User

# 1. تعريف البلوبرينت الخاص بالإدارة
# تم تحديد template_folder ليتوافق مع هيكلية المجلدات لديك
admin_bp = Blueprint('admin_panel', __name__, template_folder='templates')

# 2. مسار تسجيل الدخول (Login)
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    # إذا كان المستخدم مسجلاً بالفعل كمدير، يتم توجيهه للوحة التحكم
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin_panel.admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username, role='admin').first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'مرحباً بك يا قائد {user.username} في برج الرقابة.', 'success')
            return redirect(url_for('admin_panel.admin_dashboard'))
        else:
            flash('بيانات الدخول غير صحيحة أو ليس لديك صلاحيات إدارية.', 'danger')

    # ملاحظة: استدعاء القالب من المجلد الفرعي admin_panel
    return render_template('admin_panel/login.html')

# 3. لوحة التحكم الرئيسية (Dashboard)
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    # حماية المسار: التأكد من أن المستخدم مدير وليس مورد
    if current_user.role != 'admin':
        flash('غير مسموح للموردين بدخول برج الرقابة المركزي.', 'danger')
        return redirect(url_for('supplier_panel.supplier_login'))
    
    return render_template('admin_panel/dashboard.html')

# 4. إدارة الموردين
@admin_bp.route('/suppliers')
@login_required
def admin_suppliers_management():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    # جلب قائمة الموردين من قاعدة البيانات
    from core.models.user import User
    suppliers = User.query.filter_by(role='supplier').all()
    return render_template('admin_panel/admin_suppliers_management.html', suppliers=suppliers)

# 5. المحفظة والمالية
@admin_bp.route('/wallets')
@login_required
def wallets():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_panel/wallets.html')

# 6. تسجيل الخروج
@admin_bp.route('/logout')
@login_required
def admin_logout():
    logout_user()
    flash('تم الخروج من نظام الرقابة بنجاح.', 'info')
    return redirect(url_for('admin_panel.admin_login'))
