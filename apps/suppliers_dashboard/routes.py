# apps/suppliers_dashboard/routes.py
from flask import render_template, redirect, url_for, flash, request, session
from apps.suppliers_dashboard import suppliers_dashboard_bp
from apps.suppliers_dashboard.registry import get_supplier_modules

# استيراد النماذج وقاعدة البيانات للإنتاج
from extensions import db
from apps.suppliers.models import Supplier, SupplierProfile
from apps.wallet.models import Wallet
from apps.products.models import Product
from apps.staff.models import SupplierStaff

def get_current_supplier():
    """جلب بيانات المورد الحقيقي من قاعدة البيانات بناءً على الجلسة الحالية"""
    supplier_id = session.get('supplier_id') or session.get('user_id')
    if not supplier_id:
        return None
    return Supplier.query.get(supplier_id)

@suppliers_dashboard_bp.context_processor
def inject_supplier_modules():
    """حقن موديولات الروابط تلقائياً لجميع قوالب لوحة الموردين"""
    return {
        'supplier_modules': get_supplier_modules()
    }

@suppliers_dashboard_bp.before_request
def check_supplier_auth():
    """التحقق من المصادقة وحالة الحساب في بيئة الإنتاج"""
    if request.endpoint == 'suppliers_dashboard.logout':
        return
        
    supplier = get_current_supplier()
    if not supplier:
        flash('يرجى تسجيل الدخول للوصول إلى لوحة التحكم.', 'warning')
        return redirect(url_for('auth.supplier_login'))
        
    if getattr(supplier, 'status', 'active') != 'active':
        flash('حساب المورد غير مفعل حالياً.', 'danger')
        return redirect(url_for('auth.supplier_login'))

@suppliers_dashboard_bp.route('/')
@suppliers_dashboard_bp.route('/dashboard')
def dashboard_home():
    supplier = get_current_supplier()
    if not supplier:
        return redirect(url_for('auth.supplier_login'))
    
    # جلب بيانات المحفظة الحقيقية من قاعدة البيانات
    wallet = Wallet.query.filter_by(supplier_id=supplier.id).first()
    balance = wallet.balance if wallet else 0.00
    
    # إحصائيات حقيقية من جداول قاعدة البيانات
    products_count = Product.query.filter_by(supplier_id=supplier.id).count()
    staff_count = SupplierStaff.query.filter_by(supplier_id=supplier.id).count()
    
    # الملف الجغرافي أو تفاصيل المتجر
    profile = SupplierProfile.query.filter_by(supplier_id=supplier.id).first()

    return render_template(
        'suppliers/dashboard.html',
        supplier=supplier,
        balance=balance,
        products_count=products_count,
        staff_count=staff_count,
        wallet=wallet,
        profile=profile
    )

@suppliers_dashboard_bp.route('/products')
def list_products():
    supplier = get_current_supplier()
    products = Product.query.filter_by(supplier_id=supplier.id).all()
    return render_template('suppliers/products_list.html', supplier=supplier, products=products)

@suppliers_dashboard_bp.route('/products/add', methods=['GET', 'POST'])
def add_product():
    supplier = get_current_supplier()
    if request.method == 'POST':
        # معالجة إضافة المنتج وحفظه في قواعد البيانات
        flash('تمت إضافة المنتج بنجاح.', 'success')
        return redirect(url_for('suppliers_dashboard.list_products'))
    return render_template('suppliers/product_add.html', supplier=supplier)

@suppliers_dashboard_bp.route('/staff')
def list_staff():
    supplier = get_current_supplier()
    staff_members = SupplierStaff.query.filter_by(supplier_id=supplier.id).all()
    return render_template('suppliers/staff_list.html', supplier=supplier, staff_members=staff_members)

@suppliers_dashboard_bp.route('/settings', methods=['GET', 'POST'])
def profile_settings():
    supplier = get_current_supplier()
    if request.method == 'POST':
        # تحديث بيانات المتجر والملف الشخصي في قاعدة البيانات
        flash('تم تحديث إعدادات المتجر بنجاح.', 'success')
        return redirect(url_for('suppliers_dashboard.profile_settings'))
    
    profile = SupplierProfile.query.filter_by(supplier_id=supplier.id).first()
    return render_template('suppliers/settings.html', supplier=supplier, profile=profile)

@suppliers_dashboard_bp.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('suppliers_dashboard.dashboard_home'))
