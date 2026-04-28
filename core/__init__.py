from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from core import db
from core.models.user import User
# استيراد المنطق البرمجي للتحقق من الهوية
from .auth_logic import handle_supplier_auth

# 1. تعريف البلوبرينت الخاص ببوابة الموردين
supplier_bp = Blueprint('supplier_panel', __name__, template_folder='templates')

# 2. مسار تسجيل الدخول للموردين
@supplier_bp.route('/login', methods=['GET', 'POST'])
def supplier_login():
    # إذا كان المورد مسجلاً دخوله بالفعل، يتم توجيهه للوحة التحكم
    if current_user.is_authenticated and current_user.role == 'supplier':
        return redirect(url_for('supplier_panel.supplier_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # استخدام وظيفة التحقق السيادية
        user = handle_supplier_auth(username, password)
        
        if user:
            # تم التحقق بنجاح
            flash(f'أهلاً بك يا {user.username} في المنصة اللامركزية', 'success')
            return redirect(url_for('supplier_panel.supplier_dashboard'))
        # في حال الفشل، الرسالة تظهر من داخل handle_supplier_auth عبر flash

    return render_template('supplier_login.html')

# 3. لوحة تحكم المورد (محمية)
@supplier_bp.route('/dashboard')
@login_required
def supplier_dashboard():
    # التأكد من أن الداخل هو مورد وليس رتبة أخرى
    if current_user.role != 'supplier':
        flash('عذراً، هذه المنطقة مخصصة للموردين فقط.', 'error')
        return redirect(url_for('admin_panel.admin_login'))
        
    return render_template('supplier_dashboard.html', user=current_user)

# 4. تسجيل الخروج
@supplier_bp.route('/logout')
@login_required
def supplier_logout():
    logout_user()
    flash('تم تسجيل الخروج من بوابة الموردين بنجاح.', 'info')
    return redirect(url_for('supplier_panel.supplier_login'))

# 5. مسار تجريبي للتأكد من ربط القاعدة (اختياري)
@supplier_bp.route('/status')
def system_status():
    # هنا نستخدم current_app بدلاً من استيراد app مباشرة
    app_name = current_app.config.get('SITE_NAME', 'منصة محجوب أونلاين')
    return f"بوابة الموردين تعمل ضمن نظام: {app_name}"
