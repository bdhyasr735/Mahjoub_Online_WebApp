from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from core import db
from core.models import Supplier, Product
# استيراد البلوبرنت من ملف __init__ الحالي
from . import supplier_bp

# --- 1. مسار تسجيل الدخول (بوابة الموردين) ---
# الرابط سيكون تلقائياً: /supplier/login
@supplier_bp.route('/login', methods=['GET', 'POST'])
def login():
    # إذا كان مسجلاً دخوله كمورد، نوجهه للوحة تحكمه
    if current_user.is_authenticated and session.get('user_type') == 'supplier':
        return redirect(url_for('supplier_panel.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        supplier = Supplier.query.filter_by(email=email).first()

        # التحقق من وجود المورد وتشفير كلمة السر
        if supplier and check_password_hash(supplier.password, password):
            if not supplier.is_approved:
                flash('حسابك بانتظار موافقة الإدارة السيادية.', 'warning')
                return redirect(url_for('supplier_panel.login'))
            
            session.clear()
            session['user_type'] = 'supplier'
            login_user(supplier)
            flash(f'مرحباً بك يا {supplier.name} في بوابتك التجارية.', 'success')
            return redirect(url_for('supplier_panel.dashboard'))
        else:
            flash('بيانات الدخول غير صحيحة.', 'danger')

    return render_template('supplier_panel/login.html')

# --- 2. لوحة تحكم المورد (مركزي المبيعات) ---
@supplier_bp.route('/dashboard')
@login_required
def dashboard():
    if session.get('user_type') != 'supplier':
        return redirect(url_for('supplier_panel.login'))
        
    # جلب منتجات المورد الحالي فقط
    my_products = Product.query.filter_by(supplier_id=current_user.id).all()
    return render_template('supplier_panel/dashboard.html', products=my_products)

# --- 3. تسجيل الخروج ---
@supplier_bp.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('supplier_panel.login'))
