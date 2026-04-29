from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from core import db
from core.models.user import User

# تعريف البلوبرينت مع تحديد مجلد القوالب المحلي
admin_bp = Blueprint('admin_panel', __name__, template_folder='templates')

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
        flash('بيانات الدخول غير صحيحة', 'danger')

    # Flask سيبحث داخل admin_panel/templates/admin_panel/login.html
    return render_template('admin_panel/login.html')

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('supplier_panel.supplier_login'))
    return render_template('admin_panel/dashboard.html')
