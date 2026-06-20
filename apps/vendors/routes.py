from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet

@vendors_bp.route('/dashboard')
@vendor_login_required
def dashboard():
    """لوحة تحكم المورد (جلب البيانات الحقيقية من الجداول)"""
    # البحث عن المورد بناءً على الإيميل المخزن في الجلسة
    vendor = Supplier.query.filter_by(_owner_email=session.get('vendor_email')).first()
    
    if not vendor:
        return "بيانات المورد غير موجودة", 404
        
    return render_template(
        'vendor/dashboard.html', 
        vendor=vendor,
        wallet=vendor.wallet # جلب المحفظة المرتبطة بالمورد
    )
