from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user
from core.models.user import User

def handle_admin_login():
    """منطق التحقق المركزي لسيادة القائد علي محجوب"""
    
    # 1. إذا كان القائد مسجلاً بالفعل، نوجهه فوراً للمركز
    if current_user.is_authenticated:
        if getattr(current_user, 'role', '').lower() == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # البحث عن المستخدم
        user = User.query.filter_by(username=username).first()
        
        if not user:
            flash("⚠️ عذراً، هذا المستخدم غير مسجل في النظام.", "danger")
            return render_template('login.html') # تأكد من المسار هنا
        
        # التحقق من كلمة المرور
        if not user.check_password(password):
            flash("❌ كلمة المرور غير صحيحة، حاول مجدداً.", "warning")
            return render_template('login.html')
        
        # التحقق من الصلاحيات (الرتبة الإدارية)
        if getattr(user, 'role', '').lower() != 'admin':
            flash("🚫 الوصول مرفوض: الحساب لا يملك صلاحيات إدارية.", "danger")
            return render_template('login.html')

        # التحقق من حالة الحساب
        if not getattr(user, 'is_active_account', True):
            flash("🔒 الحساب موقوف حالياً، يرجى مراجعة الدعم.", "info")
            return render_template('login.html')
            
        # تسجيل الدخول بنجاح
        login_user(user)
        return redirect(url_for('admin.admin_dashboard'))
            
    # العرض الأولي للبوابة
    # ملاحظة: إذا كان ملف login.html داخل مجلد admin، استبدله بـ 'admin/login.html'
    return render_template('login.html')
