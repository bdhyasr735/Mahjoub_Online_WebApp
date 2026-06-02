# coding: utf-8
# 📂 apps/financial_ops/routes.py - نظام العمليات المالية والمحاسبية المحصن

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.extensions import db

# تعريف الـ Blueprint
financial_blueprint = Blueprint(
    'financial_ops', 
    __name__, 
    template_folder='templates'
)

@financial_blueprint.route('/management', methods=['GET'])
@login_required
def display_management_table():
    # 1. الاستيراد المحلي للنماذج الضرورية للبحث
    from apps.models.wallet_db import SupplierWallet as Wallet, WalletTransaction
    from apps.models.supplier_db import Supplier
    from apps.models.settlements_db import AdminSettlement

    search_query = request.args.get('search_query')
    wallet = None
    pending_withdrawals = []
    settlements = []
    
    if search_query:
        wallet = Wallet.query.join(Supplier).filter(
            (Wallet.wallet_code.ilike(f'%{search_query}%')) |
            (Supplier.username.ilike(f'%{search_query}%')) |
            (Supplier.owner_name.ilike(f'%{search_query}%'))
        ).first()
        
        if wallet:
            pending_withdrawals = WalletTransaction.query.filter_by(
                wallet_id=wallet.id, status='قيد الانتظار'
            ).order_by(WalletTransaction.created_at.desc()).all()
            
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
    # 2. الاستيراد المحلي للنماذج الضرورية للمعالجة المالية
    from apps.models.wallet_db import WalletTransaction
    from apps.models.settlements_db import AdminSettlement
    from apps.models.statement_db import SupplierStatement

    tx = WalletTransaction.query.get_or_404(tx_id)
    
    try:
        if decision == 'approve':
            ref_number = request.form.get('ref_number', 'N/A')
            financial_entity = request.form.get('financial_entity', 'N/A')
            
            new_settlement = AdminSettlement(
                wallet_id=tx.wallet_id,
                wallet_code=tx.wallet.wallet_code,
                settlement_code=AdminSettlement.generate_settlement_code(),
                settlement_type='سحب رصيد',
                currency='SAR',
                amount=tx.amount,
                reference_number=ref_number,
                financial_entity=financial_entity,
                reason_notes=f"تسوية سحب للمورد {tx.wallet.supplier.trade_name}",
                status='منفذة'
            )
            db.session.add(new_settlement)
            db.session.flush()
            
            last_stmt = SupplierStatement.query.filter_by(supplier_id=tx.wallet.supplier.id)\
                                           .order_by(SupplierStatement.created_at.desc()).first()
            
            current_balance = float(last_stmt.running_balance) if last_stmt else 0.0
            
            new_statement = SupplierStatement(
                supplier_id=tx.wallet.supplier.id,
                wallet_id=tx.wallet_id,
                description=f"سحب رصيد - مرجع: {ref_number}",
                currency='SAR',
                debit=tx.amount, 
                credit=0.00,
                running_balance=current_balance - float(tx.amount),
                reference_type='SETTLEMENT',
                reference_id=new_settlement.id
            )
            
            tx.status = 'ناجحة'
            db.session.add(new_statement)
            db.session.commit()
            
            return render_template('admin/settlement_notice.html', tx=tx, settlement=new_settlement)
        
        else:
            tx.status = 'مرفوضة'
            db.session.commit()
            flash("تم رفض العملية بنجاح", "warning")
            
    except Exception as e:
        db.session.rollback()
        flash(f"حدث خطأ أثناء المعالجة: {str(e)}", "danger")
        
    return redirect(url_for('financial_ops.display_management_table', search_query=tx.wallet.wallet_code))

@financial_blueprint.route('/settlement/create', methods=['POST'])
@login_required
def create_settlement():
    flash("تم تجهيز منطق إنشاء السند الإداري", "info")
    return redirect(url_for('financial_ops.display_management_table'))
