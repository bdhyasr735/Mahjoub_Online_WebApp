from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
# استيراد موديل المستخدم من الترسانة المركزية
from core.models.user import User 

# 1. تعريف البلوبرنت مع تحديد مجلد القوالب بدقة
admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """
    صفحة تسجيل دخول الإدارة مع التحقق المنطقي من البيانات.
    """
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # البحث عن المستخدم في قاعدة البيانات أولاً
        user = User.query.filter_by(username=username).first()
        
        # --- بداية المنطق التفصيلي للأخطاء ---
        if not user:
            # الحالة 1: المستخدم غير موجود نهائياً
            flash('عفواً.. "معرف القائد" الذي أدخلته غير مسجل في النظام.', 'danger')
        
        elif not user.is_admin:
            # الحالة 2: المستخدم موجود لكنه لا يملك صلاحيات مدير
            flash('ليس لديك صلاحية الوصول إلى برج الرقابة المركزية.', 'warning')
            
        elif not user.check_password(password):
            # الحالة 3: اسم المستخدم صحيح لكن كلمة المرور خاطئة
            flash('خطأ في "مفتاح التشفير".. يرجى التأكد من كلمة المرور.', 'danger')
            
        else:
            # الحالة 4: كل البيانات صحيحة
            login_user(user)
            return redirect(url_for('admin.admin_dashboard'))
        # --- نهاية المنطق التفصيلي ---
            
    return render_template('login.html')

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    """
    لوحة التحكم لإدارة الموردين والعمليات.
    """
    if not current_user.is_admin:
        flash('يجب تسجيل الدخول بصلاحيات مدير للوصول للوحة التحكم.', 'danger')
        return redirect(url_for('admin.admin_login'))
    
    return render_template('dashboard.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج من النظام بنجاح.', 'success')
    return redirect(url_for('admin.admin_login'))
