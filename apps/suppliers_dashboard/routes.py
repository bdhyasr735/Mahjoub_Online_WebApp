# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from functools import wraps
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

def safe_url_for(endpoint, **values):
    try:
        return url_for(endpoint, **values)
    except Exception:
        return '#'

@suppliers_bp.context_processor
def inject_global_vars():
    #متغيرات عامة آمنة للواجهات
    return dict(safe_url_for=safe_url_for)

def supplier_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'supplier_id' not in session:
            flash('يرجى تسجيل الدخول أولاً للوصول إلى لوحة التحكم.', 'warning')
            return redirect(url_for('suppliers_dashboard.login'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# مسارات المصادقة (إنتاج)
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
            else:
                flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
        except Exception as e:
            logger.error(f"❌ [Supplier Login DB Error]: {e}")
            flash('حدث خطأ في النظام، يرجى المحاولة لاحقاً.', 'danger')
            
    return render_template('suppliers/login.html')


@suppliers_bp.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('suppliers_dashboard.login'))


# ==========================================
# لوحة التحكم الرئيسية (Dashboard - نظيفة وديناميكية)
# ==========================================

@suppliers_bp.route('/')
@suppliers_bp.route('/dashboard')
@supplier_login_required
def dashboard():
    supplier_id = session.get('supplier_id')
    
    supplier_obj = None
    wallet_obj = None
    profile_obj = None
    products_count = 0
    staff_count = 0
    balance = 0.0

    try:
        from apps.models.supplier_db import Supplier, SupplierStaff, SupplierProfile
        from apps.models.wallet_db import SupplierWallet
        from apps.models.product_db import Product

        # جلب البيانات الحقيقية فقط من قاعدة البيانات
        supplier_obj = Supplier.query.get(supplier_id)
        wallet_obj = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        profile_obj = SupplierProfile.query.filter_by(supplier_id=supplier_id).first()

        if wallet_obj:
            balance = float(getattr(wallet_obj, 'balance', getattr(wallet_obj, 'balance_sar', 0.0)))

        if hasattr(Product, 'supplier_id'):
            products_count = db.session.query(db.func.count(Product.id)).filter_by(supplier_id=supplier_id).scalar() or 0

        if hasattr(SupplierStaff, 'supplier_id'):
            staff_count = db.session.query(db.func.count(SupplierStaff.id)).filter_by(supplier_id=supplier_id).scalar() or 0

    except Exception as e:
        logger.error(f"❌ [Supplier Dashboard Production Error]: {e}")

    # تجهيز هيكل البيانات للرندر بدون أي بيانات وهمية أو حقن نوافذ غريبة
    supplier = {
        'id': supplier_obj.id if supplier_obj else supplier_id,
        'username': getattr(supplier_obj, 'username', session.get('supplier_username', '')),
        'store_name': getattr(supplier_obj, 'store_name', None),
        'trade_name': getattr(supplier_obj, 'trade_name', None),
        'owner_name': getattr(supplier_obj, 'owner_name', None),
        'supplier_code': getattr(supplier_obj, 'supplier_code', None),
        'email': getattr(supplier_obj, 'email', None),
        'phone': getattr(supplier_obj, 'phone', None),
        'rank': getattr(supplier_obj, 'rank', 'bronze')
    }
    
    wallet = {
        'wallet_code': getattr(wallet_obj, 'wallet_code', None),
        'balance': balance
    }
    
    profile = {
        'city': getattr(profile_obj, 'city', None)
    }

    context = {
        "supplier": supplier,
        "wallet": wallet,
        "balance": balance,
        "products_count": products_count,
        "staff_count": staff_count,
        "profile": profile
    }

    return render_template('suppliers/dashboard.html', **context)
