from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from core import db
from core.models import Supplier, Product
from . import supplier_bp # استيراد البلوبرنت من ملف __init__.py الخاص بالمجلد

# --- مسار تسجيل الدخول للمورد ---
@supplier_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # إذا كان مسجلاً بالفعل، نوجهه للداشبورد مباشرة
        return redirect(url_for('supplier_panel.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        supplier = Supplier.query.filter_by(email=email).first()
        
        # ملاحظة: في النسخة النهائية يفضل استخدام تشفير كلمات المرور
        if supplier and supplier.password == password:
            login_user(supplier)
            flash(f'مرحباً بك يا {supplier.name} في بوابة شركاء النجاح', 'success')
            return redirect(url_for('supplier_panel.dashboard'))
        else:
            flash('بيانات الدخول غير صحيحة، يرجى التحقق من البريد وكلمة المرور', 'danger')
            
    return render_template('login.html')

# --- لوحة تحكم المورد ---
@supplier_bp.route('/')
@supplier_bp.route('/dashboard')
@login_required
def dashboard():
    # التحقق من أن المستخدم الحالي هو مورد (وليس مدير)
    if not isinstance(current_user, Supplier):
        logout_user()
        flash('هذه البوابة مخصصة للموردين فقط.', 'warning')
        return redirect(url_for('supplier_panel.login'))
        
    # جلب منتجات المورد الحالي فقط لضمان الخصوصية
    my_products = Product.query.filter_by(supplier_id=current_user.id).all()
    return render_template('dashboard.html', products=my_products)

# --- نافذة رفع منتج جديد (سعر التكلفة) ---
@supplier_bp.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not isinstance(current_user, Supplier):
        return redirect(url_for('supplier_panel.login'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        cost_price = request.form.get('cost_price') # سعر التكلفة المرفوع من المورد
        image_url = request.form.get('image_url')
        
        # إنشاء كائن المنتج مع ربطه بآيدي المورد الحالي
        new_product = Product(
            name=name,
            description=description,
            original_price=float(cost_price) if cost_price else 0.0,
            sale_price=0.0, # الإدارة هي من تضع سعر البيع لاحقاً
            image_url=image_url,
            supplier_id=current_user.id,
            status='pending', # يبقى معلقاً للمراجعة السيادية
            is_synced=False   # لا ينشر تلقائياً في قمرة
        )
        
        try:
            db.session.add(new_product)
            db.session.commit()
            flash('✅ تم إرسال المنتج لغرفة العمليات المركزية للمراجعة بنجاح.', 'success')
            return redirect(url_for('supplier_panel.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'⚠️ حدث خطأ أثناء الحفظ: {str(e)}', 'danger')

    return render_template('add_product.html')

# --- تسجيل الخروج من بوابة المورد ---
@supplier_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج من نظام الموردين بنجاح.', 'info')
    return redirect(url_for('supplier_panel.login'))
