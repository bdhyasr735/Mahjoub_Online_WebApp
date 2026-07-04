# coding: utf-8
# 📂 apps/admin_financial_management/routes.py

from flask import Blueprint, render_template, request
from flask_login import login_required
from apps.models.wallet_db import SupplierWallet  # تأكد من أن هذا المسار يطابق موقع الموديل لديك

# تعريف الـ Blueprint
financial_bp = Blueprint(
    'financial_bp', 
    __name__, 
    template_folder='templates'
)

@financial_bp.route('/wallets', methods=['GET'])
@login_required
def manage_wallets():
    """
    صفحة إدارة المحافظ المالية.
    تم جلب البيانات مع الترقيم لتتوافق مع متطلبات القالب.
    """
    # الحصول على رقم الصفحة الحالية من الرابط، الافتراضي هو 1
    page = request.args.get('page', 1, type=int)
    
    # جلب المحافظ مع الترقيم (20 عنصر في الصفحة)
    pagination = SupplierWallet.query.paginate(page=page, per_page=20, error_out=False)
    
    # تمرير البيانات للقالب (wallets للقائمة، و pagination لأزرار الترقيم)
    return render_template(
        'admin_financial_management/admin_financial_management.html',
        wallets=pagination.items,
        pagination=pagination
    )
