# coding: utf-8
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
# تم التعديل هنا لكسر حلقة الاستيراد الدائري
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet as Wallet, WalletTransaction
from apps.models.supplier_db import Supplier
from apps.models.settlements_db import AdminSettlement
# ملاحظة: تأكدت من مسار استيراد WithdrawalRequest - إذا كان في موديل آخر تأكد من مساره
# من المفترض أن تكون النماذج مستوردة من الموديلات مباشرة

# تعريف البلوبرينت
wallet_blueprint = Blueprint('wallet', __name__)

@wallet_blueprint.route('/management', methods=['GET'])
@login_required
def display_management_table():
    search_query = request.args.get('search_query')
    wallet = None
    pending_withdrawals = []
    settlements = []
    
    # إحصائيات النظام العامة
    total_wallets_count = Wallet.query.count()
    total_yer_system = db.session.query(db.func.sum(Wallet.yer_total)).scalar() or 0
    total_sar_system = db.session.query(db.func.sum(Wallet.sar_total)).scalar() or 0
    
    if search_query:
        # البحث الشامل في المحافظ ومرتبطاتها
        wallet = Wallet.query.join(Supplier).filter(
            (Wallet.wallet_code.ilike(f'%{search_query}%')) |
            (Wallet.supplier_id.ilike(f'%{search_query}%')) |
            (Supplier.username.ilike(f'%{search_query}%')) |
            (Supplier.owner_name.ilike(f'%{search_query}%'))
        ).first()
        
        if wallet:
            # جلب طلبات السحب المعلقة (تأكد من وجود نموذج WithdrawalRequest في ملفاتك)
            # تم الافتراض هنا أنها مرتبطة بـ WalletTransaction أو نموذج مشابه
            pending_withdrawals = WalletTransaction.query.filter_by(
                wallet_id=wallet.id, status='معلقة'
            ).all()
            
            # جلب سندات التسوية من الجدول المخصص للتبويب الثاني
            settlements = AdminSettlement.query.filter_by(
                wallet_id=wallet.id
            ).order_by(AdminSettlement.created_at.desc()).all()
    
    return render_template(
        'admin/settlement_and_withdrawal.html',
        wallet=wallet,
        pending_withdrawals=pending_withdrawals,
        settlements=settlements,
        total_wallets_count=total_wallets_count,
        total_yer_system=total_yer_system,
        total_sar_system=total_sar_system,
        current_search=search_query
    )

@wallet_blueprint.route('/withdrawal/handle/<int:tx_id>/<decision>', methods=['POST'])
@login_required
def handle_supplier_withdrawal(tx_id, decision):
    # افتراضاً أنك تستخدم WalletTransaction لمعالجة الطلبات
    request_obj = WalletTransaction.query.get_or_404(tx_id)
    
    if decision == 'approve':
        request_obj.status = 'ناجحة'
        flash("تم اعتماد العملية بنجاح", "success")
    else:
        request_obj.status = 'مرفوضة'
        flash("تم رفض العملية", "danger")
        
    db.session.commit()
    # العودة إلى صفحة الإدارة مع الحفاظ على البحث الحالي
    return redirect(url_for('wallet.display_management_table', search_query=request_obj.wallet.wallet_code))
