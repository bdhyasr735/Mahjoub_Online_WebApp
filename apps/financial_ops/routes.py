# coding: utf-8
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet as Wallet, WalletTransaction
from apps.models.supplier_db import Supplier
from apps.models.settlements_db import AdminSettlement

# تعريف البلوبرينت
financial_blueprint = Blueprint(
    'financial_ops', 
    __name__, 
    template_folder='templates'
)

@financial_blueprint.route('/management', methods=['GET'])
@login_required
def display_management_table():
    search_query = request.args.get('search_query')
    wallet = None
    pending_withdrawals = []
    settlements = []
    
    if search_query:
        # البحث الشامل
        wallet = Wallet.query.join(Supplier).filter(
            (Wallet.wallet_code.ilike(f'%{search_query}%')) |
            (Wallet.supplier_id.ilike(f'%{search_query}%')) |
            (Supplier.username.ilike(f'%{search_query}%')) |
            (Supplier.owner_name.ilike(f'%{search_query}%'))
        ).first()
        
        if wallet:
            # طلبات السحب (التي تحتاج لاعتماد)
            pending_withdrawals = WalletTransaction.query.filter_by(
                wallet_id=wallet.id
            ).order_by(WalletTransaction.created_at.desc()).all()
            
            # سجلات التسويات (باستخدام العلاقة الجديدة)
            settlements = AdminSettlement.query.filter_by(
                wallet_id=wallet.id
            ).order_by(AdminSettlement.created_at.desc()).all()
    
    return render_template(
        'admin/settlement_and_withdrawal.html',
        wallet=wallet,
        pending_withdrawals=pending_withdrawals,
        settlements=settlements,
        current_search=search_query
    )

@financial_blueprint.route('/withdrawal/handle/<int:tx_id>/<decision>', methods=['POST'])
@login_required
def handle_supplier_withdrawal(tx_id, decision):
    request_obj = WalletTransaction.query.get_or_404(tx_id)
    
    if decision == 'approve':
        request_obj.status = 'ناجحة'
        flash("تم اعتماد العملية بنجاح", "success")
    else:
        request_obj.status = 'مرفوضة'
        flash("تم رفض العملية", "danger")
        
    db.session.commit()
    return redirect(url_for('financial_ops.display_management_table', search_query=request_obj.wallet.wallet_code))

# مسار مستقبلي لإنشاء سند تسوية جديد
@financial_blueprint.route('/settlement/create', methods=['POST'])
@login_required
def create_settlement():
    # هنا سيتم إضافة منطق إنشاء السند لاحقاً
    flash("تم تجهيز منطق إنشاء السند", "info")
    return redirect(url_for('financial_ops.display_management_table'))
