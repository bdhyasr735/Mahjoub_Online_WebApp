# admin_panel/auth.py
from flask import render_template, request, flash, redirect, url_for
from .auth_logic import AdminAuthLogic

def login_view():
    """هذه هي الدالة التي يطلبها ملف routes.py لفتح صفحة الدخول"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # استدعاء العقل المدبر للتحقق من البيانات
        success, message, user = AdminAuthLogic.authenticate_admin(username, password)
        
        if success:
            # توجيه القائد إلى لوحة التحكم
            return redirect(url_for('admin.dashboard'))
        else:
            # إظهار رسالة الخطأ في واجهة الموقع
            flash(message, 'danger')
            
    # عرض صفحة الدخول (تأكد من وجود ملف login.html في templates/admin)
    return render_template('admin/login.html')
