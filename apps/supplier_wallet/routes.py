# coding: utf-8
# 📂 apps/supplier_wallet/routes.py

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
# تم التعديل هنا لاستيراد الخدمة مباشرة من ملف services لتجنب Circular Import
from apps.supplier_wallet.services import WalletService

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
    # جلب معرف المورد من المستخدم الحالي المسجل
    # يرجى التأكد أن نموذج المستخدم (User Model) يحتوي على حقل supplier_id
    supplier_id = getattr(current_user, 'supplier_id', None)
    
    if not supplier_id:
        # إيقاف الوصول إذا لم يكن المستخدم مرتبطاً بمورد
        abort(403, description="لا تملك صلاحية الوصول إلى هذه المحفظة.")

    # جلب بيانات المحفظة من خلال خدمة المحفظة
    wallet = WalletService.get_supplier_wallet(supplier_id)
    
    if not wallet:
        # في حال لم تكن هناك محفظة منشأة للمورد
        abort(404, description="لم يتم العثور على محفظة مرتبطة بحسابك.")

    # عرض القالب مع تمرير بيانات المحفظة
    return render_template('supplier_wallet/supplier_wallet.html', wallet=wallet)

# ملاحظة: إذا كان المورد سيقوم بطلبات مالية (مثل طلب سحب)، 
# يمكنك إضافة مسار هنا يستخدم WalletService.process_transaction
