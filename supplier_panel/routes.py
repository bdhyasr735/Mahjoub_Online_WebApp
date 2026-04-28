from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app
from flask_login import login_user, logout_user, login_required, current_user
from core import db
from core.models.user import User
# استيراد منطق التحقق (تأكد من وجود هذا الملف في نفس المجلد)
try:
    from .auth_logic import handle_supplier_auth
except ImportError:
    # دالة احتياطية في حال تعذر استيراد المنطق الخارجي مؤقتاً
    def handle_supplier_auth(username, password):
        user = User.query.filter_by(username=username, role='supplier').first()
        if user and user.check_password(password):
            return user
        return None

# 1. تعريف البلوبرينت (Blueprint)
# تم تحديد template_folder لضمان التعرف على ملفات الـ HTML داخل المجلد الفرعي
supplier_bp = Blueprint('supplier_panel', __name__, template_folder='templates')

# 2. مسار تسجيل الدخول (Login)
@supplier_bp.route('/login', methods=['GET', 'POST'])
def supplier_login():
    # منع المستخدم المسجل بالفعل من العودة لصفحة الدخول
    if current_user.is_authenticated:
        if current_user.role == 'supplier':
            return redirect(url_for('supplier_panel.supplier_dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin_panel.admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # استدعاء منطق التحقق السيادي
        user = handle_supplier_auth(username, password)
        
        if user:
            if user.status == 'approved':
                login_user(user)
                flash(f'مرحباً بك في نظام التوريد، {user.username}', 'success')
                return redirect(url_for('supplier_panel.supplier_dashboard'))
            else:
                flash('حسابك قيد المراجعة من قبل الإدارة المركزية.', 'warning')
        else:
            flash('بيانات الدخول غير صحيحة أو الحساب غير مسجل كمورد.', 'danger')

    return render_template('supplier_login.html')

# 3. لوحة تحكم المورد (Dashboard)
# لاحظ أن الاسم هنا هو 'supplier_dashboard' ليتطابق مع url_for
@supplier_bp.route('/dashboard')
@login_required
def supplier_dashboard():
    # فحص الرتبة لضمان أمن النظام السيادي
    if current_user.role != 'supplier':
        flash('وصول غير مصرح به لبرج الموردين.', 'danger')
        return redirect(url_for('admin_panel.admin_login'))
        
    return render_template('supplier_dashboard.html', user=current_user)

# 4. تسجيل الخروج (Logout)
@supplier_bp.route('/logout')
@login_required
def supplier_logout():
    logout_user()
    flash('تم إنهاء الجلسة اللامركزية بنجاح.', 'info')
    return redirect(url_for('supplier_panel.supplier_login'))
