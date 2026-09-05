# -*- coding: utf-8 -*-
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, session
from flask_login import login_required, current_user, login_user, logout_user
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.supplier_profile_db import SupplierProfile
from apps.extensions import db

# إنشاء Blueprint متوافق مع هيكلة المسارات والجداول مع دعم الرابط المنتهي بـ /
suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    template_folder='templates',
    url_prefix='/supplier/dashboard'
)


# ============================================
# دالة مساعدة لتوليد الروابط بشكل آمن
# ============================================
@suppliers_dashboard_bp.context_processor
def utility_processor():
    def safe_url_for(endpoint, **values):
        try:
            return url_for(endpoint, **values)
        except Exception:
            return '#'
    return dict(safe_url_for=safe_url_for)


# ============================================
# مسار تسجيل الدخول المؤقت (للتجربة)
# ============================================
@suppliers_dashboard_bp.route('/login', strict_slashes=False)
def login():
    """صفحة تسجيل دخول مؤقتة للتجربة"""
    try:
        # إذا كان المستخدم مسجل دخول بالفعل، انتقل إلى الداشبورد
        if current_user.is_authenticated:
            return redirect(url_for('suppliers_dashboard.index'))
        
        # جلب أول مورد في قاعدة البيانات
        supplier = Supplier.query.first()
        if supplier:
            login_user(supplier)
            flash(f"تم تسجيل الدخول بنجاح كمورد: {supplier.username}", "success")
            return redirect(url_for('suppliers_dashboard.index'))
        else:
            return "لا يوجد مورد في قاعدة البيانات. يرجى إنشاء مورد أولاً.", 404
    except Exception as e:
        return f"خطأ في تسجيل الدخول: {str(e)}", 500


# ============================================
# مسار تسجيل الخروج
# ============================================
@suppliers_dashboard_bp.route('/logout', strict_slashes=False)
@login_required
def logout():
    """تسجيل الخروج"""
    logout_user()
    session.clear()
    flash("تم تسجيل الخروج بنجاح.", "info")
    return redirect(url_for('suppliers_dashboard.login'))


# ============================================
# الصفحة الرئيسية للوحة التحكم
# ============================================
@suppliers_dashboard_bp.route('/', strict_slashes=False)
@login_required
def index():
    """الصفحة الرئيسية للوحة تحكم المورد متوافقة تماماً مع الجداول ونموذج المحفظة."""
    try:
        # 1. التحقق الآمن من مصادقة المستخدم
        if not current_user.is_authenticated:
            flash("يرجى تسجيل الدخول للوصول إلى لوحة التحكم.", "warning")
            return redirect(url_for('suppliers_dashboard.login'))

        # 2. استخراج معرّف المورد
        supplier_id = None
        
        if hasattr(current_user, 'supplier_id') and current_user.supplier_id:
            supplier_id = current_user.supplier_id
        elif hasattr(current_user, 'id'):
            if isinstance(current_user, Supplier):
                supplier_id = current_user.id
            else:
                possible_supplier = db.session.get(Supplier, current_user.id)
                if possible_supplier:
                    supplier_id = current_user.id
                else:
                    supplier_id = getattr(current_user, 'supplier_id', None)

        if not supplier_id:
            flash("يرجى تسجيل الدخول بحساب مورد صحيح للوصول إلى لوحة التحكم.", "warning")
            return redirect(url_for('suppliers_dashboard.login'))

        # 3. جلب بيانات المورد
        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            flash("لم يتم العثور على بيانات المورد المرتبطة.", "danger")
            return redirect(url_for('suppliers_dashboard.login'))
        
        # 4. جلب المحفظة المالية
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        
        # إنشاء محفظة إذا لم تكن موجودة
        if not wallet:
            import string, secrets
            wallet_code = f"WLT-{supplier_id}-{''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))}"
            wallet = SupplierWallet(
                wallet_code=wallet_code,
                supplier_id=supplier_id,
                status='active',
                balance_sar=0.00
            )
            db.session.add(wallet)
            db.session.commit()

        # 5. جلب عدد المنتجات المرتبطة
        products_count = 0
        try:
            products_count = ProductSupplierMapping.query.filter_by(
                supplier_id=supplier_id,
                is_active=True
            ).count()
        except Exception:
            products_table = db.metadata.tables.get('products')
            if products_table is not None:
                products_count = db.session.execute(
                    db.select(db.func.count(products_table.c.id))
                    .where(products_table.c.supplier_id == supplier_id)
                ).scalar() or 0

        # 6. جلب عدد الموظفين المرتبطين
        staff_count = 0
        try:
            staff_count = SupplierStaff.query.filter_by(
                supplier_id=supplier_id,
                is_active=True
            ).count()
        except Exception:
            staff_table = db.metadata.tables.get('supplier_staff')
            if staff_table is not None:
                staff_count = db.session.execute(
                    db.select(db.func.count(staff_table.c.id))
                    .where(staff_table.c.supplier_id == supplier_id)
                ).scalar() or 0

        # 7. جلب الملف الشخصي المرتبط
        profile = SupplierProfile.query.filter_by(supplier_id=supplier_id).first()
        
        # 8. الرصيد
        balance = float(wallet.balance_sar or 0.0) if wallet else 0.0
        
        # 9. قائمة الوحدات الجانبية (sidebar)
        supplier_modules = {
            'suppliers_dashboard': {
                'title': 'لوحة التحكم',
                'icon': 'fas fa-chart-pie',
                'links': {
                    'suppliers_dashboard.index': 'الرئيسية'
                }
            },
            'supplier_products': {
                'title': 'إدارة المنتجات',
                'icon': 'fas fa-box',
                'links': {
                    'supplier_products.index': 'جميع المنتجات',
                    'supplier_products.add': 'إضافة منتج جديد'
                }
            },
            'supplier_orders': {
                'title': 'المبيعات والطلبات',
                'icon': 'fas fa-shopping-cart',
                'links': {
                    'supplier_orders.index': 'الطلبات الواردة',
                    'supplier_orders.history': 'سجل المبيعات'
                }
            },
            'supplier_wallet': {
                'title': 'الإدارة المالية',
                'icon': 'fas fa-wallet',
                'links': {
                    'supplier_wallet.index': 'المحفظة والسحب',
                    'supplier_wallet.reports': 'تقارير التسوية'
                }
            },
            'supplier_staff': {
                'title': 'الموظفين',
                'icon': 'fas fa-users',
                'links': {
                    'supplier_staff.index': 'قائمة الموظفين',
                    'supplier_staff.add': 'إضافة موظف'
                }
            }
        }
        
        # 10. تجهيز القالب
        rendered_html = render_template(
            'suppliers/dashboard.html',
            page_title='لوحة تحكم المورد | محجوب أونلاين',
            supplier=supplier,
            profile=profile,
            wallet=wallet,
            balance=balance,
            products_count=products_count,
            staff_count=staff_count,
            supplier_modules=supplier_modules
        )
        
        response = make_response(rendered_html)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    except Exception as e:
        db.session.rollback()
        print(f"❌ [خطأ في لوحة تحكم الموردين]: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"حدث خطأ داخلي في الخادم: {str(e)}", 500
