from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from core.models import Supplier, Product
from . import supplier_bp 
from .auth_logic import verify_supplier_credentials # التأكد من وجود النقطة قبل auth_logic

# --- 1. مسار تسجيل الدخول اللامركزي ---
@supplier_bp.route('/login', methods=['GET', 'POST'])
def login():
    # منع المورد المسجل دخولاً بالفعل من رؤية صفحة الدخول مرة أخرى
    if current_user.is_authenticated:
        if hasattr(current_user, 'email') and not hasattr(current_user, 'role'): # تمييز المورد عن الأدمن
            return redirect(url_for('supplier_panel.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('يرجى ملء كافة الحقول السيادية للدخول.', 'warning')
            return render_template('supplier_login.html')

        # استدعاء المحقق الخارجي
        message, category, supplier = verify_supplier_credentials(username, password)
        
        flash(message, category)

        if supplier: 
            # تنفيذ عملية تسجيل الدخول الرسمية
            login_user(supplier)
            return redirect(url_for('supplier_panel.dashboard'))
            
    return render_template('supplier_login.html')

# --- 2. لوحة التحكم المحمية (الترسانة) ---
@supplier_bp.route('/dashboard')
@login_required
def dashboard():
    # فحص أمني: التأكد أن المستخدم "مورد" وليس "أدمن" يحاول التسلل
    # نستخدم التحقق من وجود حقل "wallet_balance" الذي ينفرد به المورد
    if not hasattr(current_user, 'wallet_balance'):
        logout_user()
        flash('عذراً، هذه المنطقة مخصصة للموردين المعتمدين فقط.', 'danger')
        return redirect(url_for('supplier_panel.login'))
        
    # جلب منتجات المورد المرتبطة برقم محفظته MAH-9046
    my_products = Product.query.filter_by(supplier_id=current_user.id).all()
    
    return render_template('supplier_dashboard.html', products=my_products)

# --- 3. خروج المورد ---
@supplier_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج من نظام الترسانة بنجاح.', 'info')
    return redirect(url_for('supplier_panel.login'))
