# apps/suppliers_dashboard/routes.py
from flask import render_template, redirect, url_for, flash, request, session
from apps.suppliers_dashboard import suppliers_dashboard_bp
from apps.suppliers_dashboard.registry import get_supplier_modules

# محاكاة لجلب بيانات المورد الحالي (يمكن استبدالها لاحقاً بنظام المصالحة وقواعد البيانات الخاصة بك)
def get_current_supplier():
    # بيانات افتراضية متوافقة مع القوالب التي أنشأتها
    return {
        'id': 1,
        'username': 'mahjoub_store',
        'store_name': 'متجر محجوب المركزية',
        'trade_name': 'مؤسسة محجوب للتجارة الإلكترونية',
        'owner_name': 'علي محجوب',
        'supplier_code': 'SUP-9081',
        'email': 'supplier@mahjoub.cloud',
        'phone': '+967770000000',
        'rank': 'gold',
        'status': 'active'
    }

@suppliers_dashboard_bp.context_processor
def inject_supplier_modules():
    """حقن موديولات الروابط تلقائياً لجميع قوالب لوحة الموردين"""
    return {
        'supplier_modules': get_supplier_modules()
    }

@suppliers_dashboard_bp.route('/')
@suppliers_dashboard_bp.route('/dashboard')
def dashboard_home():
    supplier = get_current_supplier()
    
    # بيانات افتراضية للإحصائيات (يمكن ربطها بقواعد البيانات مباشرة)
    balance = 15420.50
    products_count = 128
    staff_count = 5
    
    wallet = {
        'wallet_code': 'WAL-SUP-8842'
    }
    
    profile = {
        'city': 'الحديدية / صنعاء'
    }

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
    return render_template('suppliers/products_list.html', supplier=supplier)

@suppliers_dashboard_bp.route('/products/add')
def add_product():
    supplier = get_current_supplier()
    return render_template('suppliers/product_add.html', supplier=supplier)

@suppliers_dashboard_bp.route('/staff')
def list_staff():
    supplier = get_current_supplier()
    return render_template('suppliers/staff_list.html', supplier=supplier)

@suppliers_dashboard_bp.route('/settings')
def profile_settings():
    supplier = get_current_supplier()
    return render_template('suppliers/settings.html', supplier=supplier)

@suppliers_dashboard_bp.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('suppliers_dashboard.dashboard_home'))
