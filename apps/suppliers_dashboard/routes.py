# -*- coding: utf-8 -*-
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.supplier_profile_db import SupplierProfile
from apps.extensions import db

# إنشاء Blueprint متوافق مع هيكلة المسارات والجداول
suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    template_folder='templates',
    url_prefix='/supplier/dashboard'
)


@suppliers_dashboard_bp.route('/')
@login_required
def index():
    """الصفحة الرئيسية للوحة تحكم المورد متوافقة تماماً مع الجداول ونموذج المحفظة."""
    try:
        # التحقق من أن المستخدم يمتلك معرف صحيح
        if not hasattr(current_user, 'id'):
            flash("يرجى تسجيل الدخول كمورد.", "warning")
            return redirect(url_for('suppliers_auth_portal.login_page'))
        
        # التعامل الآمن مع معرف المورد سواء كان دخله كمورد رئيسي أو موظف تابع
        supplier_id = getattr(current_user, 'supplier_id', None)
        if not supplier_id and hasattr(current_user, 'id'):
            if isinstance(current_user, Supplier):
                supplier_id = current_user.id
            else:
                supplier_id = current_user.id

        # جلب بيانات المورد باستخدام db.session.get المتوافقة مع SQLAlchemy 3.x
        supplier = db.session.get(Supplier, supplier_id) if supplier_id else None
        if not supplier:
            flash("لم يتم العثور على بيانات المورد.", "danger")
            return redirect(url_for('suppliers_auth_portal.login_page'))
        
        # جلب المحفظة المالية المرتبطة بالمورد بالريال السعودي (SAR)
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        
        # إذا لم تكن المحفظة موجودة، يتم إنشاؤها تلقائياً بالرمز والخصائص المعيارية
        if not wallet:
            import string, secrets
            wallet_code = f"WLT-{supplier_id}-{ ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4)) }"
            wallet = SupplierWallet(
                wallet_code=wallet_code,
                supplier_id=supplier_id,
                status='active',
                balance_sar=0.00
            )
            db.session.add(wallet)
            db.session.commit()

        # جلب عدد المنتجات المرتبطة
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

        # جلب عدد الموظفين المرتبطين بالمورد
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

        # جلب الملف الشخصي المرتبط
        profile = SupplierProfile.query.filter_by(supplier_id=supplier_id).first()
        
        # الاعتماد الحصري على balance_sar
        balance = float(wallet.balance_sar or 0.0) if wallet else 0.0
        
        # قائمة الوحدات الجانبية (sidebar) بتصميم المنصة
        supplier_modules = [
            {
                'name': 'الرئيسية',
                'icon': 'fa-chart-pie',
                'items': [
                    {'name': 'لوحة التحكم', 'url': url_for('suppliers_dashboard.index'), 'active': True}
                ]
            },
            {
                'name': 'إدارة المنتجات',
                'icon': 'fa-box',
                'items': [
                    {'name': 'جميع المنتجات', 'url': '#', 'active': False},
                    {'name': 'إضافة منتج جديد', 'url': '#', 'active': False}
                ]
            },
            {
                'name': 'المبيعات والطلبات',
                'icon': 'fa-shopping-cart',
                'items': [
                    {'name': 'الطلبات الواردة', 'url': '#', 'active': False},
                    {'name': 'سجل المبيعات', 'url': '#', 'active': False}
                ]
            },
            {
                'name': 'الإدارة المالية',
                'icon': 'fa-wallet',
                'items': [
                    {'name': 'المحفظة والسحب', 'url': '#', 'active': False},
                    {'name': 'تقارير التسوية', 'url': '#', 'active': False}
                ]
            },
            {
                'name': 'الموظفين',
                'icon': 'fa-users',
                'items': [
                    {'name': 'قائمة الموظفين', 'url': '#', 'active': False},
                    {'name': 'إضافة موظف', 'url': '#', 'active': False}
                ]
            }
        ]
        
        # الاستدعاء الصريح المباشر للقالب بالمسار الواضح
        return render_template(
            'suppliers_auth_portal/dashboard/supplier_dashboard.html',
            page_title='لوحة تحكم المورد | محجوب أونلاين',
            supplier=supplier,
            profile=profile,
            wallet=wallet,
            balance=balance,
            products_count=products_count,
            staff_count=staff_count,
            supplier_modules=supplier_modules
        )
    except Exception as e:
        db.session.rollback()
        print(f"❌ [خطأ في لوحة تحكم الموردين]: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"حدث خطأ داخلي في الخادم: {str(e)}", 500
