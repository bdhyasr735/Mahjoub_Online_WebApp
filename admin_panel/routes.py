from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import admin_panel 
from core.models import User, Supplier, Product, db
from core.utils.security import admin_required

# --- 1. بوابة الولوج السيادي ---
@admin_panel.route('/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and hasattr(current_user, 'role') and current_user.role == 'admin':
        return redirect(url_for('admin_panel.admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username, role='admin').first()

        if user and user.check_password(password):
            login_user(user)
            flash('تم تفعيل الولوج السيادي بنجاح.. أهلاً بك أيها القائد.', 'success')
            return redirect(url_for('admin_panel.admin_dashboard'))
        else:
            flash('فشل في التحقق من الهوية.. تأكد من المعرف أو مفتاح التشفير.', 'danger')

    return render_template('login.html')

# --- 2. برج الرقابة المركزية (Dashboard) ---
@admin_panel.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'orders_count': 0, 
        's_count': Supplier.query.count(),
        'total_balance': 0.00, 
        'p_count': Product.query.count()
    }
    return render_template('dashboard.html', **stats, transactions=[])

# --- 3. إنهاء الجلسة الآمنة ---
@admin_panel.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم إغلاق البوابة السيادية بنجاح.', 'info')
    return redirect(url_for('admin_panel.admin_login'))
