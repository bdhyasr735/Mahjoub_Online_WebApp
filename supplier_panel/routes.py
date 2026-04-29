from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from core.models.user import User

supplier_bp = Blueprint('supplier_panel', __name__, template_folder='templates')

@supplier_bp.route('/login', methods=['GET', 'POST'])
def supplier_login():
    if current_user.is_authenticated and current_user.is_supplier():
        return redirect(url_for('supplier_panel.supplier_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_supplier():
            if user.is_approved():
                login_user(user)
                return redirect(url_for('supplier_panel.supplier_dashboard'))
            flash('حسابك قيد المراجعة.', 'info')
        else:
            flash('بيانات الدخول غير صحيحة.', 'danger')
    return render_template('supplier_panel/supplier_login.html')

@supplier_bp.route('/dashboard')
@login_required
def supplier_dashboard():
    if not current_user.is_supplier():
        return redirect(url_for('supplier_panel.supplier_login'))
    return render_template('supplier_panel/dashboard.html')

@supplier_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('supplier_panel.supplier_login'))
