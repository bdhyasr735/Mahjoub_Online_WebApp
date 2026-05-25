# coding: utf-8
# 📂 apps/financial_ops/routes.py
from flask import render_template, request, redirect, url_for, flash
from apps.financial_ops import blueprint
from apps.extensions import db
from apps.models.settlements_db import AdminSettlement
# استبدل هذه الاستيرادات بما يناسب هيكل مشروعك (Withdrawal/SupplierWallet)
from apps.models.withdrawals_db import Withdrawal 

@blueprint.route('/management')
def settlement_and_withdrawal():
    """عرض لوحة التحكم المركزية مع التبويبات والبيانات"""
    pending_withdrawals = Withdrawal.query.filter_by(status='pending').all()
    settlements = AdminSettlement.query.order_by(AdminSettlement.created_at.desc()).all()
    
    return render_template(
        'admin/settlement_and_withdrawal.html',
        pending_withdrawals=pending_withdrawals,
        settlements=settlements
    )

@blueprint.route('/withdrawal/handle/<int:tx_id>/<decision>', methods=['POST'])
def handle_supplier_withdrawal(tx_id, decision):
    """معالجة طلب السحب وحفظ بيانات التسوية المادية"""
    tx = Withdrawal.query.get_or_404(tx_id)
    
    if decision == 'approve':
        # استقبال البيانات من المودال التفاعلي
        ref_number = request.form.get('ref_number')
        financial_entity = request.form.get('financial_entity')
        
        # 1. إنشاء سند تسوية إداري في الجدول المخصص
        new_settlement = AdminSettlement(
            wallet_id=tx.wallet_id,
            wallet_code=tx.wallet.wallet_code,
            settlement_code=AdminSettlement.generate_settlement_code(),
            settlement_type='سحب رصيد',
            currency='SAR', # أو العملة المعتمدة
            amount=tx.amount,
            reference_number=ref_number,
            financial_entity=financial_entity,
            reason_notes=f"تسوية سحب معتمد للمورد {tx.wallet.supplier.name}",
            status='منفذة'
        )
        
        # 2. تحديث حالة طلب السحب
        tx.status = 'approved'
        
        db.session.add(new_settlement)
        db.session.commit()
        
        flash(f"تم اعتماد العملية بنجاح. رقم السند: {new_settlement.settlement_code}", "success")
        
    return redirect(url_for('financial_ops.settlement_and_withdrawal'))
