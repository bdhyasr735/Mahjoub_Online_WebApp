from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from . import supplier_bp 
from .auth_logic import verify_supplier_credentials
from .decorators import sovereign_approval_required 
from core import db
from core.models.product import Product
from core.models.supplier import Supplier
# استيراد محرك جلب الأقسام من قمرة ليعرضها للمورد عند إضافة منتج
from services.qumra_handler import fetch_qumra_collections

# --- 1. بوابة الدخول للموردين ---
@supplier_bp.route('/login', methods=['GET', 'POST'])
def login():
    # منع التداخل: إذا كان المستخدم "أدمن" يحاول دخول بوابة المورد، نقوم بتطهير جلسته
    if current_user.is_authenticated:
        if session.get('user_type') == 'supplier':
            return redirect(url_for('supplier_panel.dashboard'))
        else:
            # إذا كان أدمن يحاول الدخول هنا، نسجل خروجه ليدخل بهوية مورد
            logout_user()
            session.clear()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('يرجى إدخال بيانات الهوية السيادية للمورد.', 'warning')
            return render_template('supplier_login.html')

        # استخدام المحرك الذي راجعناه سابقاً للتحقق من المورد
        message, category, supplier = verify_supplier_credentials(username, password)
        
        if supplier: 
            session.permanent = True
            session['user_type'] = 'supplier' # الختم السيادي للمورد
            login_user(supplier)
            flash(f'مرحباً بك يا {supplier.name} في منصة محجوب أونلاين.', 'success')
            return redirect(url_for('supplier_panel.dashboard'))
        else:
            flash(message, category)
            
    return render_template('supplier_login.html')

# --- 2. لوحة تحكم المورد (الترسانة الخاصة) ---
@supplier_bp.route('/dashboard')
@login_required
@sovereign_approval_required 
def dashboard():
    # التأكد من الهوية: منع الأدمن من رؤية لوحة المورد (والعكس)
    if session.get('user_type') != 'supplier':
        session.clear()
        logout_user()
        return redirect(url_for('supplier_panel.login'))
        
    try:
        # جلب المنتجات التابعة لهذا المورد فقط
        my_products = Product.query.filter_by(supplier_id=current_user.id).all()
        return render_template('dashboard.html', products=my_products)
    except Exception as e:
        return f"خطأ في استعراض البيانات: {str(e)}", 500

# --- 3. إضافة منتج جديد (الربط مع قمرة) ---
@supplier_bp.route('/add-product', methods=['GET', 'POST'])
@login_required
@sovereign_approval_required
def add_product():
    # جلب الأقسام (Collections) من قمرة لحظياً ليختار المورد القسم المناسب
    collections = fetch_qumra_collections()

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        collection_id = request.form.get('collection_id')
        cost_price = request.form.get('cost_price')
        currency = request.form.get('currency', 'YER') # الافتراضي ريال يمني
        
        if not name or not cost_price:
            flash('اسم المنتج وسعر التكلفة حقول إلزامية للتعميد.', 'danger')
            return redirect(request.url)

        try:
            # إنشاء المنتج محلياً في حالة "Pending" بانتظار مراجعة القائد علي محجوب
            new_product = Product(
                name=name,
                description=description,
                q_collection_id=collection_id,
                cost_price=float(cost_price),
                currency=currency,
                supplier_id=current_user.id,
                status='pending' 
            )
            
            db.session.add(new_product)
            db.session.commit()
            flash('✅ تم رفع المنتج بنجاح. سيتم إشعارك فور تعميده ونشره من قبل الإدارة.', 'success')
            return redirect(url_for('supplier_panel.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'⚠️ فشل الحفظ: {str(e)}', 'danger')

    return render_template('add_product.html', collections=collections)

# --- 4. غرفة الانتظار (للموردين الجدد) ---
@supplier_bp.route('/waiting-room')
@login_required
def waiting_room():
    # التحقق من قاعدة البيانات مباشرة لرؤية ما إذا كان الأدمن قد وافق على المورد
    supplier = Supplier.query.get(current_user.id)
    if supplier and supplier.is_approved:
        return redirect(url_for('supplier_panel.dashboard'))
    
    return render_template('waiting_approval.html')

# --- 5. خروج المورد وتطهير الهوية ---
@supplier_bp.route('/logout')
@login_required
def logout():
    session.clear() # مسح وسم 'supplier' من الجلسة
    logout_user()
    return redirect(url_for('supplier_panel.login'))
