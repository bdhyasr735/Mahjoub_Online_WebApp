# coding: utf-8
# 📂 apps/supplier_wallet/routes.py

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from apps.supplier_wallet import WalletService

# تعريف الـ Blueprint الخاص بالمورد
supplier_wallet_bp = Blueprint(
    'supplier_wallet', 
    __name__, 
    template_folder='templates'
)

@supplier_wallet_bp.route('/my-wallet', methods=['GET'])
@login_required
def view_my_wallet():
    """
    عرض خزانة المورد الخاصة بالمستخدم المسجل حالياً.
    نستخدم معرف المورد من current_user لضمان الخصوصية.
    """
    # نفترض أن كائن المستخدم الحالي يحتوي على supplier_id
    # يرجى تعديل 'current_user.supplier_id' بما يناسب هيكلية قاعدة بياناتك
    supplier_id = getattr(current_user, 'supplier_id', None)
    
    if not supplier_id:
        abort(403, description="لا تملك صلاحية الوصول إلى هذه المحفظة.")

    wallet = WalletService.get_supplier_wallet(supplier_id)
    
    if not wallet:
        abort(404, description="لم يتم العثور على محفظة مرتبطة بحسابك.")

    # عرض القالب مع تمرير بيانات المحفظة
    return render_template('supplier_wallet/supplier_wallet.html', wallet=wallet)

# ملاحظة: إذا كان المورد سيقوم بطلبات مالية (مثل طلب سحب)، 
# يمكنك إضافة مسار هنا يستخدم WalletService.process_transaction
