from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user, login_user
from core import db
from core.models import User

# تعريف البوابة هنا مباشرة لضمان عدم ضياع المسار
admin_bp = Blueprint('admin_panel', __name__, template_folder='templates')

# --- بوابة دخول الإدارة ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin_panel.admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username, role='admin').first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_panel.admin_dashboard'))
        else:
            flash('⚠️ فشل التحقق السيادي: بيانات الإدارة غير صحيحة.', 'danger')
            
    return render_template('admin_panel/login.html')

# --- لوحة التحكم المركزية ---
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('supplier_panel.login'))
    return render_template('admin_panel/dashboard.html')

# --- تسجيل الخروج ---
@admin_bp.route('/logout')
def admin_logout():
    logout_user()
    return redirect(url_for('admin_panel.admin_login'))
