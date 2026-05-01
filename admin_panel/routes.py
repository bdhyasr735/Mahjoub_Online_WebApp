from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from core.models.user import User 
from . import admin_bp

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    # إذا كان المستخدم مسجلاً دخوله بالفعل، يتم توجيهه حسب رتبته
    if current_user.is_authenticated:
        return redirect_by_role(current_user)
    
    if request.method == 'POST':
        # جلب البيانات من نموذج تسجيل الدخول
        username = request.form.get('username')
        password = request.form.get('password')
        
        # البحث عن المستخدم في قاعدة البيانات بواسطة اسم المستخدم
        user = User.query.filter_by(username=username).first()
        
        # التحقق من وجود المستخدم ومطابقة كلمة المرور المشفرة
        if user and user.check_password(password):
            # التأكد من أن الحساب غير معلق من قبل الإدارة
            if not user.is_active_account:
                flash('هذا الحساب معلق حالياً. يرجى مراجعة الإدارة.', 'warning')
                return redirect(url_for('admin.admin_login'))
            
            # تنفيذ عملية الدخول وتخزين الجلسة
            login_user(user)
            return redirect_by_role(user)
        
        # في حال فشل المطابقة تظهر هذه الرسالة
        flash('خطأ في اسم المستخدم أو كلمة المرور. يرجى المحاولة مرة أخرى.', 'danger')
            
    return render_template('login.html')

def redirect_by_role(user):
    """توجيه المستخدم إلى لوحة التحكم المناسبة بناءً على دوره"""
    if user.role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif user.role == 'supplier':
        return redirect(url_for('supplier.dashboard'))
    
    # توجيه افتراضي للعملاء أو الأدوار الأخرى
    return redirect(url_for('main.index'))

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    """لوحة تحكم القائد - محمية بصلاحيات الإدارة"""
    if current_user.role != 'admin':
        flash('عذراً، لا تملك صلاحيات الدخول إلى برج الرقابة.', 'danger')
        return redirect(url_for('admin.admin_login'))
    
    return render_template('dashboard.html')

@admin_bp.route('/logout')
@login_required
def logout():
    """تسجيل الخروج وإنهاء الجلسة"""
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('admin.admin_login'))
