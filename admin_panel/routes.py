from flask import render_template
from flask_login import login_required, current_user, logout_user
from . import admin_bp
from .auth import handle_admin_login

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """توجيه طلب الدخول إلى منطق المعالجة في auth.py"""
    return handle_admin_login()

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    """لوحة التحكم المركزية"""
    # بيانات تجريبية لملء الواجهة الفاخرة
    context = {
        'admin_name': current_user.username,
        'orders_count': "1,250",
        's_count': "48",
        'total_balance': "15.5K",
        'p_count': "12"
    }
    return render_template('dashboard.html', **context)

@admin_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.admin_login'))
