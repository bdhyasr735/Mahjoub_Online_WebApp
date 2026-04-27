from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from . import supplier_bp 
from core.models import User, Supplier, Product
from core import db

@supplier_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # منطق تسجيل الدخول المبسط للمورد
        username = request.form.get('username')
        user = User.query.filter_by(username=username, role='supplier').first()
        if user:
            session['user_type'] = 'supplier'
            login_user(user)
            return redirect(url_for('supplier_panel.dashboard'))
    return render_template('supplier_panel/login.html')

@supplier_bp.route('/dashboard')
@login_required
def dashboard():
    if session.get('user_type') != 'supplier':
        return redirect(url_for('supplier_panel.login'))
    products = Product.query.filter_by(supplier_id=current_user.supplier_profile.id).all()
    return render_template('supplier_panel/dashboard.html', products=products)
