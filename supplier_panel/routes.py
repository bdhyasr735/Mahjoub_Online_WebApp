from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from . import supplier_bp 
from .auth_logic import verify_supplier_credentials
from .decorators import sovereign_approval_required 
from core import db
from core.models import Product, Supplier
from core.utils.qmr_api import QmrEngine

# استدعاء محرك الربط مع قمرة
qmr = QmrEngine()

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
            
    return render_template('supplier_panel/supplier_login.html')

# --- 2. لوحة التحكم ---
@supplier_bp.route('/dashboard')
@login_required
@sovereign_approval_required 
def dashboard():
    try:
        if session.get('user_type') != 'supplier':
            session.clear()
            logout_user()
            return redirect(url_for('supplier_panel.login'))
            
        my_products = Product.query.filter_by(supplier_id=current_user.id).all()
        return render_template('supplier_panel/dashboard.html', products=my_products)
        
    except Exception as e:
        return f"خطأ في النظام السيادي: {str(e)}", 500

# --- 3. إضافة منتج جديد (الربط مع قمرة) ---
@supplier_bp.route('/add-product', methods=['GET', 'POST'])
@login_required
@sovereign_approval_required
def add_product():
    # سحب الفئات لحظياً من قمرة عبر GraphQL ليختار منها المورد
    collections = qmr.get_all_collections()

    if request.method == 'POST':
        name = request.form.get('name')
        q_product_id = request.form.get('q_product_id')
        cost_price = request.form.get('cost_price')
        currency = request.form.get('currency')
        
        if not q_product_id or not cost_price:
            flash('يرجى إدخال معرف المنتج وسعر التكلفة لضمان الربط.', 'danger')
            return redirect(request.url)

        try:
            new_product = Product(
                name=name,
                q_product_id=q_product_id,
                cost_price=float(cost_price),
                currency=currency,
                supplier_id=current_user.id,
                status='pending' # المنتج يبقى معلقاً بانتظار تعميد الإدارة
            )
            
            db.session.add(new_product)
            db.session.commit()
            flash('✅ تم رفع المنتج للترسانة بنجاح وهو بانتظار المراجعة السيادية.', 'success')
            return redirect(url_for('supplier_panel.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'⚠️ حدث خطأ أثناء الحفظ: {str(e)}', 'danger')

    return render_template('supplier_panel/add_product.html', collections=collections)

# --- 4. صفحة الانتظار ---
@supplier_bp.route('/waiting-room')
@login_required
def waiting_room():
    from core.models.supplier import Supplier
    fresh_data = Supplier.query.get(current_user.id)
    
    if fresh_data and fresh_data.is_approved:
        return redirect(url_for('supplier_panel.dashboard'))
    
    return render_template('supplier_panel/waiting_approval.html')

# --- 5. خروج المورد ---
@supplier_bp.route('/logout')
@login_required
def logout():
    session.pop('user_type', None)
    session.clear()
    logout_user()
    return redirect(url_for('supplier_panel.login'))
