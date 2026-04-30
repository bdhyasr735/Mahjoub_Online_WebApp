from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from core.models.user import User
from core.models.product import Product 
from core.models.supplier import Supplier 
from core import db

supplier_bp = Blueprint('supplier_panel', __name__, template_folder='templates')

@supplier_bp.route('/login', methods=['GET', 'POST'])
def supplier_login():
    # منع المورد المسجل دخولاً بالفعل من رؤية صفحة اللوجن
    if current_user.is_authenticated and getattr(current_user, 'role', None) == 'supplier':
        return redirect(url_for('supplier_panel.supplier_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        # التحقق من الهوية والدور
        if user and user.check_password(password) and getattr(user, 'role', None) == 'supplier':
            # التحقق من الموافقة السيادية
            if hasattr(user, 'is_approved') and user.is_approved():
                login_user(user)
                return redirect(url_for('supplier_panel.supplier_dashboard'))
            
            flash('حسابك في مرحلة التدقيق السيادي حالياً.', 'info')
        else:
            flash('بيانات الوصول غير معترف بها في الترسانة.', 'danger')
            
    return render_template('supplier_panel/supplier_login.html')

@supplier_bp.route('/dashboard')
@login_required
def supplier_dashboard():
    # حماية المسار من غير الموردين
    if getattr(current_user, 'role', None) != 'supplier':
        return redirect(url_for('supplier_panel.supplier_login'))

    # جلب بيانات المورد لربط المنتجات
    supplier_info = Supplier.query.filter_by(user_id=current_user.id).first()
    
    if not supplier_info:
        flash('لم يتم العثور على ملف مورد مرتبط بحسابك. تواصل مع الإدارة المركزية.', 'warning')
        products = []
    else:
        # جلب منتجات المورد المحددة من الترسانة
        products = Product.query.filter_by(supplier_id=supplier_info.id).all()

    return render_template(
        'supplier_panel/dashboard.html', 
        supplier=supplier_info, 
        products=products
    )

@supplier_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if getattr(current_user, 'role', None) != 'supplier':
        flash('لا تملك تصريحاً لإضافة أصول جديدة.', 'danger')
        return redirect(url_for('supplier_panel.supplier_login'))
    
    if request.method == 'POST':
        # سيتم لاحقاً دمج منطق رفع الصور وحفظ البيانات هنا
        flash('تم إرسال بيانات المنتج للترسانة بنجاح.', 'success')
        return redirect(url_for('supplier_panel.supplier_dashboard'))
        
    return render_template('supplier_panel/add_product.html')

@supplier_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تأمين الخروج من بيئة التحكم بنجاح.', 'success')
    return redirect(url_for('supplier_panel.supplier_login'))
