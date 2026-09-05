# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from functools import wraps
from datetime import datetime
import logging

# استيراد النماذج وقواعد البيانات (يتم تعديلها حسب بنية مشروعك الفعلية)
# from apps.models import db, Supplier, SupplierWallet, SupplierProduct, SupplierStaff, SupplierProfile
# from apps.extensions import limiter

logger = logging.getLogger(__name__)

suppliers_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    url_prefix='/supplier',
    template_folder='templates',
    static_folder='static'
)

# دالة مساعدة لتوفير مسارات آمنة (Safe URL for) تفادياً لأخطاء الـ endpoints غير الموجودة
def safe_url_for(endpoint, **values):
    try:
        return url_for(endpoint, **values)
    except Exception:
        return '#'

# حقن المتغيرات العامة في جميع قوالب الموردين (مثل روابط الشريط الجانبي والـ safe_url_for)
@suppliers_bp.context_processor
def inject_supplier_modules():
    modules = {
        'dashboard': {
            'title': 'لوحة التحكم',
            'icon': 'fas fa-home',
            'links': {
                'suppliers_dashboard.dashboard': 'الرئيسية'
            }
        },
        'products': {
            'title': 'إدارة المنتجات',
            'icon': 'fas fa-boxes',
            'links': {
                'suppliers_dashboard.products_list': 'قائمة المنتجات',
                'suppliers_dashboard.add_product': 'إضافة منتج جديد'
            }
        },
        'wallet': {
            'title': 'المحفظة المالية',
            'icon': 'fas fa-wallet',
            'links': {
                'suppliers_dashboard.wallet_details': 'تفاصيل المحفظة والعمليات'
            }
        },
        'staff': {
            'title': 'فريق العمل',
            'icon': 'fas fa-users-cog',
            'links': {
                'suppliers_dashboard.staff_list': 'إدارة الموظفين والصلاحيات'
            }
        },
        'settings': {
            'title': 'إعدادات المتجر',
            'icon': 'fas fa-store-alt',
            'links': {
                'suppliers_dashboard.store_settings': 'الملف الشخصي والبيانات'
            }
        }
    }
    return dict(supplier_modules=modules, safe_url_for=safe_url_for)


# ديكوراتور (Decorator) التحقق من تسجيل دخول المورد
def supplier_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'supplier_id' not in session:
            flash('يرجى تسجيل الدخول أولاً للوصول إلى لوحة التحكم.', 'warning')
            return redirect(url_for('suppliers_dashboard.login'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# مسارات المصادقة (تسجيل الدخول / الخروج)
# ==========================================

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'supplier_id' in session:
        return redirect(url_for('suppliers_dashboard.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # مثال وهمي للتحقق (يتم استبداله بالتحقق من قاعدة البيانات ونظام الـ Hashing)
        # supplier = Supplier.query.filter_by(username=username).first()
        # if supplier and supplier.check_password(password):
        if username == 'demo_supplier' and password == 'password':
            session['supplier_id'] = 1
            session['supplier_username'] = username
            flash('تم تسجيل الدخول بنجاح، أهلاً بك!', 'success')
            return redirect(url_for('suppliers_dashboard.dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
            
    return render_template('suppliers/login.html')


@suppliers_bp.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('suppliers_dashboard.login'))


# ==========================================
# لوحة التحكم الرئيسية (Dashboard)
# ==========================================

@suppliers_bp.route('/')
@suppliers_bp.route('/dashboard')
@supplier_login_required
def dashboard():
    supplier_id = session.get('supplier_id')
    
    # جلب بيانات المورد (يتم استبدالها بالاستعلام الفعلي من قاعدة البيانات)
    # supplier = Supplier.query.get_or_404(supplier_id)
    # wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    # products_count = SupplierProduct.query.filter_by(supplier_id=supplier_id).count()
    # staff_count = SupplierStaff.query.filter_by(supplier_id=supplier_id).count()
    
    # بيانات افتراضية تجريبية للتأكد من عمل القالب بسلاسة
    supplier = {
        'id': supplier_id,
        'username': session.get('supplier_username', 'mahjoub_store'),
        'store_name': 'متجر محجوب الرقمي',
        'trade_name': 'مؤسسة محجوب أونلاين للتجارة',
        'owner_name': 'علي محمد محجوب',
        'supplier_code': 'SUP-9921',
        'email': 'supplier@mahjoub.online',
        'phone': '+967711223344',
        'rank': 'gold'
    }
    
    wallet = {
        'wallet_code': 'WAL-DEV-883',
        'balance': 15420.50
    }
    
    products_count = 48
    staff_count = 5
    balance = wallet['balance']
    profile = {'city': 'الحديدية / الخوخة'}

    return render_template(
        'suppliers/dashboard.html',
        supplier=supplier,
        wallet=wallet,
        balance=balance,
        products_count=products_count,
        staff_count=staff_count,
        profile=profile
    )


# ==========================================
# مسارات المنتجات
# ==========================================

@suppliers_bp.route('/products')
@supplier_login_required
def products_list():
    supplier_id = session.get('supplier_id')
    # منطق جلب قائمة المنتجات الخاصة بالمورد
    products = [] # استبدلها بـ SupplierProduct.query.filter_by(supplier_id=supplier_id).all()
    return render_template('suppliers/products/list.html', products=products)


@suppliers_bp.route('/products/add', methods=['GET', 'POST'])
@supplier_login_required
def add_product():
    if request.method == 'POST':
        # منطق إضافة منتج جديد
        flash('تمت إضافة المنتج بنجاح وإرساله للمراجعة.', 'success')
        return redirect(url_for('suppliers_dashboard.products_list'))
    return render_template('suppliers/products/add.html')


# ==========================================
# مسار المحفظة المالية
# ==========================================

@suppliers_bp.route('/wallet/<wallet_id>')
@suppliers_bp.route('/wallet')
@supplier_login_required
def wallet_details(wallet_id='general'):
    supplier_id = session.get('supplier_id')
    # منطق جلب حركات المحفظة، الأرباح، والعمليات المالية
    transactions = []
    balance = 15420.50
    return render_template('suppliers/wallet/details.html', balance=balance, transactions=transactions, wallet_id=wallet_id)


# ==========================================
# مسار فريق العمل
# ==========================================

@suppliers_bp.route('/staff')
@supplier_login_required
def staff_list():
    supplier_id = session.get('supplier_id')
    staff_members = []
    return render_template('suppliers/staff/list.html', staff_members=staff_members)


# ==========================================
# مسار إعدادات المتجر
# ==========================================

@suppliers_bp.route('/settings', methods=['GET', 'POST'])
@supplier_login_required
def store_settings():
    supplier_id = session.get('supplier_id')
    if request.method == 'POST':
        # تحديث بيانات المتجر
        flash('تم تحديث إعدادات المتجر بنجاح.', 'success')
        return redirect(url_for('suppliers_dashboard.store_settings'))
        
    return render_template('suppliers/settings/store_settings.html')
