# admin_panel/auth.py
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user
from functools import wraps # ضروري لإنشاء أدوات الحماية
from .auth_logic import AdminAuthLogic

# --- إضافة دالة الحماية السيادية (admin_required) ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # التحقق من أن المستخدم مسجل دخول ومن أنه "أدمن"
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("⚠️ عذراً، هذه المنطقة تتطلب صلاحيات القيادة العليا.", "danger")
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def login_view():
    """دالة عرض ومعالجة الدخول"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        success, message, user = AdminAuthLogic.authenticate_admin(username, password)
        
        if success:
            login_user(user) # تسجيل الدخول فعلياً في الجلسة
            return redirect(url_for('admin.dashboard'))
        else:
            flash(message, 'danger')
            
    return render_template('admin/login.html')
