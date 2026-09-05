from flask import Blueprint, render_template
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
from apps.models.product_db import Product  # تعديل المسار حسب اسم نموذج المنتجات لديك إن وجد
from apps.models.supplier_staff_db import SupplierStaff

# تعريف البلوبرنت وتحديد مسار مجلد القوالب بدقة
suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    template_folder='templates',
    url_prefix='/supplier'
)

MODULE_NAME = "لوحة تحكم المورد"
MODULE_ICON = "fas fa-tachometer-alt"
SHOW_IN_SUPPLIER = True

NAV_ITEMS = [
    {
        "endpoint": "suppliers_dashboard.supplier_dashboard_home",
        "title": "الرئيسية",
        "icon": "fas fa-home"
    }
]

@suppliers_dashboard_bp.route('/dashboard')
@login_required
def supplier_dashboard_home():
    """عرض لوحة تحكم المورد الرئيسية"""
    supplier_id = getattr(current_user, 'supplier_id', None) or getattr(current_user, 'id', None)
    
    supplier_obj = db.session.get(Supplier, supplier_id) if supplier_id else None
    wallet_obj = SupplierWallet.query.filter_by(supplier_id=supplier_id).first() if supplier_id else None
    
    products_count = 0
    staff_count = 0
    
    if supplier_id:
        try:
            products_count = Product.query.filter_by(supplier_id=supplier_id).count()
        except Exception:
            pass
            
        try:
            staff_count = SupplierStaff.query.filter_by(supplier_id=supplier_id).count()
        except Exception:
            pass

    balance = getattr(wallet_obj, 'balance', 0.0) if wallet_obj else 0.0

    return render_template(
        'suppliers/dashboard.html',
        supplier=supplier_obj,
        wallet=wallet_obj,
        balance=balance,
        products_count=products_count,
        staff_count=staff_count
    )

def register_module(app):
    """دالة التسجيل التلقائي المطلوبة بواسطة create_app"""
    app.register_blueprint(suppliers_dashboard_bp)
    print("✅ [مجلد الموردين]: تم تسجيل موديلو لوحة تحكم الموردين بنجاح.")
