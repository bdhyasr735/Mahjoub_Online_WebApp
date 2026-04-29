from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
# استيراد الموديل من النواة
from core.models.user import User

# تعريف البلوبرينت مع تحديد مجلد القوالب
admin_bp = Blueprint(
    'admin_panel', 
    __name__, 
    template_folder='templates'
)

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """منطق تسجيل دخول الإدارة الموحد"""
    # 1. إذا كان المسؤول مسجلاً دخوله بالفعل، توجه للوحة التحكم
    if current_user.is_authenticated and current_user.is_admin():
        return redirect(url_for('admin_panel.admin_dashboard'))

    if request.method == 'POST':
        # استخدام username ليتطابق مع موديل User
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # البحث عن المستخدم في قاعدة البيانات
        user = User.query.filter_by(username=username).first()

        # 2. التحقق من الهوية والصلاحية الإدارية
        if user and user.check_password(password) and user.is_admin():
            login_user(user, remember=remember)
            return redirect(url_for('admin_panel.admin_dashboard'))
        
        # رسالة خطأ واضحة
        flash('بيانات الدخول غير صحيحة أو لا تملك صلاحيات إدارية.', 'danger')

    # ملاحظة: يجب أن يكون المسار 'admin_panel/login.html' ليتوافق مع هيكليتك
    return render_template('admin_panel/login.html')

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    """لوحة التحكم المركزية - تتطلب تسجيل دخول وصلاحية أدمن"""
    if not current_user.is_admin():
        flash('هذه المنطقة مخصصة لمدير النظام فقط.', 'warning')
        return redirect(url_for('admin_panel.admin_login'))
    
    return render_template('admin_panel/dashboard.html')

@admin_bp.route('/logout')
@login_required
def logout():
    """تسجيل خروج آمن للمسؤول"""
    logout_user()
    flash('تم تسجيل الخروج من لوحة الإدارة.', 'info')
    return redirect(url_for('admin_panel.admin_login'))
