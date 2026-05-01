from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from core.models.user import User 
from . import admin_bp

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        # التأكد من هوية المستخدم وحالة حسابه السيادية
        if user and user.check_password(password):
            if not user.is_active_account:
                flash('هذا الحساب معلق حالياً، يرجى مراجعة الإدارة.', 'warning')
                return redirect(url_for('admin.admin_login'))
            
            login_user(user)
            return redirect_by_role(user)
        else:
            flash('فشل التوثيق.. تأكد من المعرف ومفتاح التشفير.', 'danger')
            
    return render_template('login.html')

def redirect_by_role(user):
    """توجيه المستخدم بناءً على الحوكمة التي حددتها في الموديل"""
    if user.role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif user.role == 'supplier':
        # تأكد من إنشاء هذا البلوبرنت لاحقاً للموردين في عدن والمخا
        return redirect(url_for('supplier.dashboard'))
    else:
        # العملاء يوجهون للمتجر الرئيسي
        return redirect(url_for('main.index'))

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    # حماية برج الرقابة من أي دور آخر غير 'admin'
    if current_user.role != 'admin':
        flash('غير مصرح لك بدخول برج الرقابة.', 'danger')
        return redirect(url_for('admin.admin_login'))
    return render_template('dashboard.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم إنهاء الجلسة، نراك لاحقاً في منصة محجوب.', 'success')
    return redirect(url_for('admin.admin_login'))
