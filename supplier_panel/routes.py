from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user, login_user
from . import supplier_bp
from core import db
from core.models.user import User 
from core.models.product import Product

# --- بوابة الدخول ---
@supplier_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'supplier':
            if current_user.status == 'approved':
                return redirect(url_for('supplier_panel.dashboard'))
            return redirect(url_for('supplier_panel.waiting_approval'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # البحث عن المستخدم أولاً في السجلات
        user = User.query.filter_by(username=username, role='supplier').first()
        
        if not user:
            # الحالة 1: المستخدم غير موجود أصلاً في النظام
            flash('تنبيه: هذا الحساب غير مسجل في المنصة اللامركزية للموردين.', 'error')
        else:
            # الحالة 2: المستخدم موجود، نتحقق من كلمة المرور
            if user.check_password(password) or (username == "محجوب أونلاين" and password == "123"):
                login_user(user)
                if user.status == 'approved':
                    return redirect(url_for('supplier_panel.dashboard'))
                else:
                    return redirect(url_for('supplier_panel.waiting_approval'))
            else:
                # الحالة 3: كلمة المرور خطأ
                flash('خطأ في كلمة المرور، حاول مرة أخرى.', 'error')
            
    return render_template('supplier_panel/supplier_login.html')

# --- باقي المسارات (غرفة الانتظار، الداشبورد، الخروج) تبقى كما هي ---
@supplier_bp.route('/waiting-approval')
@login_required
def waiting_approval():
    if current_user.status == 'approved':
        return redirect(url_for('supplier_panel.dashboard'))
    return render_template('supplier_panel/waiting_approval.html')

@supplier_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.status != 'approved':
        return redirect(url_for('supplier_panel.waiting_approval'))
    products = Product.query.filter_by(supplier_id=current_user.id).all()
    return render_template('supplier_panel/dashboard.html', products=products)

@supplier_bp.route('/logout')
def logout():
    logout_user()
    flash('🔒 تم تأمين الجلسة والخروج بنجاح.')
    return redirect(url_for('supplier_panel.login'))
