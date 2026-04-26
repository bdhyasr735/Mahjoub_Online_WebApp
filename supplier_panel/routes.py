from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from . import supplier_bp 
from .auth_logic import verify_supplier_credentials
from .decorators import sovereign_approval_required 

# --- 1. مسار تسجيل الدخول السيادي ---
@supplier_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if session.get('user_type') == 'supplier':
            return redirect(url_for('supplier_panel.dashboard'))
        else:
            logout_user()
            session.clear()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('يرجى ملء كافة الحقول السيادية للدخول.', 'warning')
            return render_template('supplier_panel/supplier_login.html')

        message, category, supplier = verify_supplier_credentials(username, password)
        
        if supplier: 
            session.permanent = True
            session['user_type'] = 'supplier'
            login_user(supplier)
            flash(f'تم الولوج بنجاح.. أهلاً بك يا {supplier.name}', 'success')
            return redirect(url_for('supplier_panel.dashboard'))
        else:
            flash(message, category)
            
    # التأكد من المسار الصحيح للقالب لتجنب خطأ 500
    return render_template('supplier_panel/supplier_login.html')

# --- 2. لوحة التحكم ---
@supplier_bp.route('/dashboard')
@login_required
@sovereign_approval_required 
def dashboard():
    from core.models.product import Product
    try:
        if session.get('user_type') != 'supplier':
            session.clear()
            logout_user()
            return redirect(url_for('supplier_panel.login'))
            
        my_products = Product.query.filter_by(supplier_id=current_user.id).all()
        
        # استدعاء القالب من المجلد الفرعي المخصص للموردين
        return render_template('supplier_panel/dashboard.html', products=my_products)
        
    except Exception as e:
        return f"خطأ في النظام السيادي: {str(e)}", 500

# --- 3. صفحة الانتظار ---
@supplier_bp.route('/waiting-room')
@login_required
def waiting_room():
    from core.models.supplier import Supplier
    fresh_data = Supplier.query.get(current_user.id)
    
    if fresh_data and fresh_data.is_approved:
        return redirect(url_for('supplier_panel.dashboard'))
    
    return render_template('supplier_panel/waiting_approval.html')

# --- 4. خروج المورد ---
@supplier_bp.route('/logout')
@login_required
def logout():
    session.pop('user_type', None)
    session.clear()
    logout_user()
    return redirect(url_for('supplier_panel.login'))
