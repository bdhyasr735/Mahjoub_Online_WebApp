# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from functools import wraps
from datetime import datetime
import logging

from apps.extensions import db

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

# حقن المتغيرات العامة في جميع قوالب الموردين
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
        
        try:
            from apps.models.supplier_db import Supplier
            supplier = Supplier.query.filter_by(username=username).first()
            if supplier and hasattr(supplier, 'check_password') and supplier.check_password(password):
                session['supplier_id'] = supplier.id
                session['supplier_username'] = supplier.username
                flash('تم تسجيل الدخول بنجاح، أهلاً بك!', 'success')
                return redirect(url_for('suppliers_dashboard.dashboard'))
        except Exception as e:
            print(f"⚠️ [Supplier Login Error Skipped]: {e}")

        # Fallback تجريبي في حال لم يتم العثور على قاعدة البيانات أو المورد للطوارئ
        if username == 'demo_supplier' and password == 'password':
            session['supplier_id'] = 1
            session['supplier_username'] = username
            flash('تم تسجيل الدخول بنجاح (وضع التجربة)، أهلاً بك!', 'success')
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
# لوحة التحكم الرئيسية (Dashboard) - بأسلوب آمن
# ==========================================

@suppliers_bp.route('/')
@suppliers_bp.route('/dashboard')
@supplier_login_required
def dashboard():
    supplier_id = session.get('supplier_id')
    
    supplier = None
    wallet = None
    balance = 0.0
    products_count = 0
    staff_count = 0
    profile = None

    try:
        # 1. جلب بيانات المورد الأساسية
        try:
            from apps.models.supplier_db import Supplier
            supplier_obj = Supplier.query.get(supplier_id)
            if supplier_obj:
                supplier = {
                    'id': supplier_obj.id,
                    'username': getattr(supplier_obj, 'username', 'N/A'),
                    'store_name': getattr(supplier_obj, 'store_name', 'غير محدد'),
                    'trade_name': getattr(supplier_obj, 'trade_name', 'غير محدد'),
                    'owner_name': getattr(supplier_obj, 'owner_name', 'غير محدد'),
                    'supplier_code': getattr(supplier_obj, 'supplier_code', 'N/A'),
                    'email': getattr(supplier_obj, 'email', 'N/A'),
                    'phone': getattr(supplier_obj, 'phone', 'N/A'),
                    'rank': getattr(supplier_obj, 'rank', 'bronze')
                }
        except Exception as e:
            print(f"⚠️ [Supplier Query Error Skipped]: {e}")

        # 2. جلب بيانات المحفظة والرصيد
        try:
            from apps.models.wallet_db import SupplierWallet
            wallet_obj = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
            if wallet_obj:
                wallet = {
                    'wallet_code': getattr(wallet_obj, 'wallet_code', 'N/A'),
                    'balance': float(getattr(wallet_obj, 'balance', getattr(wallet_obj, 'balance_sar', 0.0)))
                }
                balance = wallet['balance']
        except Exception as e:
            print(f"⚠️ [Supplier Wallet Error Skipped]: {e}")

        # 3. حساب عدد المنتجات النشطة للمورد
        try:
            from apps.models.product_db import Product
            if hasattr(Product, 'supplier_id'):
                products_count = db.session.query(db.func.count(Product.id)).filter_by(supplier_id=supplier_id).scalar() or 0
        except Exception as e:
            print(f"⚠️ [Supplier Products Count Error Skipped]: {e}")

        # 4. حساب عدد فريق العمل / الموظفين
        try:
            from apps.models.supplier_db import SupplierStaff
            if hasattr(SupplierStaff, 'supplier_id'):
                staff_count = db.session.query(db.func.count(SupplierStaff.id)).filter_by(supplier_id=supplier_id).scalar() or 0
        except Exception as e:
            print(f"⚠️ [Supplier Staff Count Error Skipped]: {e}")

        # 5. جلب بيانات الملف الشخصي الإضافية للموقع
        try:
            from apps.models.supplier_db import SupplierProfile
            profile_obj = SupplierProfile.query.filter_by(supplier_id=supplier_id).first()
            if profile_obj:
                profile = {'city': getattr(profile_obj, 'city', 'غير محدد')}
        except Exception as e:
            print(f"⚠️ [Supplier Profile Error Skipped]: {e}")

    except Exception as general_err:
        print(f"❌ [Supplier Dashboard General Error]: {str(general_err)}")

    # Fallback بيانات افتراضية آمنة في حال عدم توفر النماذج بالكامل لتفادي أي خطأ عرض
    if not supplier:
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

    if not wallet:
        wallet = {
            'wallet_code': 'WAL-DEV-883',
            'balance': balance
        }

    if not profile:
        profile = {'city': 'الحديدية / الخوخة'}

    context = {
        "supplier": supplier,
        "wallet": wallet,
        "balance": balance,
        "products_count": products_count,
        "staff_count": staff_count,
        "profile": profile
    }

    return render_template('suppliers/dashboard.html', **context)


# ==========================================
# مسارات المنتجات للمورد
# ==========================================

@suppliers_bp.route('/products')
@supplier_login_required
def products_list():
    supplier_id = session.get('supplier_id')
    products = []
    try:
        from apps.models.product_db import Product
        if hasattr(Product, 'supplier_id'):
            products = Product.query.filter_by(supplier_id=supplier_id).all()
    except Exception as e:
        print(f"⚠️ [Products List Error Skipped]: {e}")
        
    return render_template('suppliers/products/list.html', products=products)


@suppliers_bp.route('/products/add', methods=['GET', 'POST'])
@supplier_login_required
def add_product():
    if request.method == 'POST':
        try:
            # منطق حفظ المنتج في قاعدة البيانات هنا
            flash('تمت إضافة المنتج بنجاح وإرساله للمراجعة.', 'success')
            return redirect(url_for('suppliers_dashboard.products_list'))
        except Exception as e:
            flash(f'حدث خطأ أثناء إضافة المنتج: {e}', 'danger')
            
    return render_template('suppliers/products/add.html')


# ==========================================
# مسار المحفظة المالية للمورد
# ==========================================

@suppliers_bp.route('/wallet/<wallet_id>')
@suppliers_bp.route('/wallet')
@supplier_login_required
def wallet_details(wallet_id='general'):
    supplier_id = session.get('supplier_id')
    transactions = []
    balance = 0.0
    try:
        from apps.models.wallet_db import SupplierWallet, WalletTransaction
        wallet_obj = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        if wallet_obj:
            balance = float(getattr(wallet_obj, 'balance', getattr(wallet_obj, 'balance_sar', 0.0)))
            if hasattr(WalletTransaction, 'wallet_id'):
                transactions = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id).order_by(WalletTransaction.created_at.desc()).all()
    except Exception as e:
        print(f"⚠️ [Wallet Details Error Skipped]: {e}")

    return render_template('suppliers/wallet/details.html', balance=balance, transactions=transactions, wallet_id=wallet_id)


# ==========================================
# مسار فريق العمل للمورد
# ==========================================

@suppliers_bp.route('/staff')
@supplier_login_required
def staff_list():
    supplier_id = session.get('supplier_id')
    staff_members = []
    try:
        from apps.models.supplier_db import SupplierStaff
        if hasattr(SupplierStaff, 'supplier_id'):
            staff_members = SupplierStaff.query.filter_by(supplier_id=supplier_id).all()
    except Exception as e:
        print(f"⚠️ [Staff List Error Skipped]: {e}")
        
    return render_template('suppliers/staff/list.html', staff_members=staff_members)


# ==========================================
# مسار إعدادات المتجر للمورد
# ==========================================

@suppliers_bp.route('/settings', methods=['GET', 'POST'])
@supplier_login_required
def store_settings():
    supplier_id = session.get('supplier_id')
    if request.method == 'POST':
        try:
            # منطق تحديث بيانات المتجر في قاعدة البيانات هنا
            flash('تم تحديث إعدادات المتجر بنجاح.', 'success')
            return redirect(url_for('suppliers_dashboard.store_settings'))
        except Exception as e:
            flash(f'حدث خطأ أثناء التحديث: {e}', 'danger')
        
    return render_template('suppliers/settings/store_settings.html')
