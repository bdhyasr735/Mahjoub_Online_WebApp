from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user
from sqlalchemy.exc import OperationalError
from core.models.user import User  # موديل بيانات القائد
from . import admin_bp

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    # إذا كان القائد مسجلاً بالفعل، يتم تحويله للوحة التحكم فوراً
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        # استقبال البيانات من واجهة login.html
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        try:
            # البحث عن "علي" في سجلات المنصة اللامركزية
            user = User.query.filter_by(username=username).first()
            
            if not user:
                # رسالة: المستخدم غير موجود
                flash('⚠️ معرف القائد غير مسجل في المنصة اللامركزية.', 'warning')
            elif not user.check_password(password):
                # رسالة: كلمة المرور غير صحيحة
                flash('❌ مفتاح التشفير (كلمة المرور) غير مطابق لسجلاتنا.', 'danger')
            else:
                # نجاح الولوج السيادي
                login_user(user)
                return redirect(url_for('admin.admin_dashboard'))
                
        except OperationalError:
            # رسالة: تعذر الوصول للسيرفر أو قاعدة البيانات
            flash('🚨 فشل الاتصال بالقاعدة المركزية، يرجى التحقق من استقرار السيرفر.', 'danger')
            
    return render_template('login.html')

@admin_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.admin_login'))
