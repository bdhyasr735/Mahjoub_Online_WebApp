# -*- coding: utf-8 -*-
"""
📂 apps/wallet/approvals_and_settlements.py
مركز الرقابة والتسويات المادية - لوحة تحكم الإدارة المركزية (2026)
منصة محجوب أونلاين - سوقك الذكي
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from datetime import datetime

# 🌟 التصحيح الحاسم: استدعاء محرك قواعد البيانات من الامتدادات المشتركة وليس من جذر التطبيق القديم
from apps.extensions import db 

# استيراد نماذج الجداول السيادية (الأب والابن)
from apps.wallet.models import Wallet, WalletTransaction, AdminSettlement

# تعريف الـ Blueprint بالاسم المعتمد في المنظومة
wallet_blueprint = Blueprint('wallet', __name__, template_folder='templates')


@wallet_blueprint.route('/admin/governance/table', methods=['GET'])
def display_management_table():
    """
    1️⃣ الدالة الرئيسية: عرض جدول موافقة الطلبات والتسوية المالية
    تقوم بحساب الإحصائيات الشاملة للنظام وتدقيق أصول المحافظ المستدعاة
    """
    search_query = request.args.get('search_query', '').strip()
    
    # حساب الأرصدة السيادية الشاملة في النظام بالكامل لشرط العرض الإحصائي
    total_wallets_count = Wallet.query.count()
    
    # تجميع كلي للأرصدة في المنصة لضمان مراقبة السيولة الكلية لعام 2026
    total_yer_system = db.session.query(db.func.sum(Wallet.yer_available)).scalar() or 0.0
    total_sar_system = db.session.query(db.func.sum(Wallet.sar_available)).scalar() or 0.0
    total_usd_system = db.session.query(db.func.sum(Wallet.usd_available)).scalar() or 0.0

    # جلب كافة طلبات السحب النقدي المرفوعة والتي حالتها "معلقة" حصراً من جدول الأب
    pending_withdrawals = WalletTransaction.query.filter_by(
        transaction_type='withdrawal', 
        status='pending'
    ).order_by(WalletTransaction.created_at.desc()).all()

    wallet = None
    wallet_settlements = []

    # مسار البحث والحوكمة الاستكشافية عند إدخال معرف أو كود محفظة
    if search_query:
        wallet = Wallet.query.filter(
            (Wallet.wallet_code == search_query) | 
            (Wallet.supplier_id == search_query)
        ).first()

        if wallet:
            # استدعاء أرشيف السندات الاستثنائية للابن المرتبطة بهذه المحفظة فقط
            wallet_settlements = AdminSettlement.query.filter_by(
                wallet_code=wallet.wallet_code
            ).order_by(AdminSettlement.created_at.desc()).all()
        else:
            flash(f"تنبيه حوكمي: لا يوجد كيان مالي مسجل في النظام يطابق: {search_query}", "warning")

    return render_template(
        'admin/settlement_and_withdrawal.html',
        total_wallets_count=total_wallets_count,
        total_yer_system=total_yer_system,
        total_sar_system=total_sar_system,
        total_usd_system=total_usd_system,
        pending_withdrawals=pending_withdrawals,
        wallet=wallet,
        wallet_settlements=wallet_settlements,
        current_search=search_query
    )


@wallet_blueprint.route('/admin/withdrawal/decision/<int:tx_id>/<string:decision>', methods=['POST'])
def handle_supplier_withdrawal(tx_id, decision):
    """
    2️⃣ دالة حوكمة طلبات السحب: اتخاذ قرار بشري بالتعميد والصرف أو الرفض العكسي
    """
    transaction = WalletTransaction.query.get_or_404(tx_id)
    wallet = Wallet.query.get(transaction.wallet_id)
    
    if transaction.status != 'pending':
        flash("هذه الحركة المالية تم تعميدها واتخاذ قرار بشأنها مسبقاً في النظام.", "danger")
        return redirect(url_for('wallet.display_management_table'))

    currency_attr = transaction.currency.lower()  # yer, sar, usd

    if decision == 'approve':
        # في حالة التعميد: تحويل المبلغ من المعلق إلى المسحوبات النهائية بشكل دائم
        current_pending = getattr(wallet, f"{currency_attr}_pending") or 0.0
        setattr(wallet, f"{currency_attr}_pending", max(0.0, current_pending - transaction.amount))
        
        current_withdrawn = getattr(wallet, f"{currency_attr}_withdrawn") or 0.0
        setattr(wallet, f"{currency_attr}_withdrawn", current_withdrawn + transaction.amount)
        
        transaction.status = 'approved'
        transaction.completed_at = datetime.utcnow()
        db.session.commit()
        flash(f"تم تعميد وصرف مبلغ {transaction.amount:,.2f} {transaction.currency} بنجاح وتحويل الحركة إلى مسحوبات نهائية.", "success")

    elif decision == 'reject':
        # في حالة الرفض البشري: فك حجز الرصيد وإعادته فوراً للرصيد المتاح للمورد
        current_pending = getattr(wallet, f"{currency_attr}_pending") or 0.0
        setattr(wallet, f"{currency_attr}_pending", max(0.0, current_pending - transaction.amount))
        
        current_available = getattr(wallet, f"{currency_attr}_available") or 0.0
        setattr(wallet, f"{currency_attr}_available", current_available + transaction.amount)
        
        transaction.status = 'rejected'
        transaction.completed_at = datetime.utcnow()
        db.session.commit()
        flash(f"تم رفض طلب السحب المالي وإرجاع كامل الرصيد المحجوز إلى حساب المورد المتاح.", "info")

    return redirect(url_for('wallet.display_management_table'))


@wallet_blueprint.route('/admin/settlement/execute/<string:wallet_code>', methods=['POST'])
def execute_admin_settlement(wallet_code):
    """
    3️⃣ دالة إصدار السندات الاستثنائية: قيد شحن أو خصم عكسي يدوي بواسطة الإدارة
    """
    wallet = Wallet.query.filter_by(wallet_code=wallet_code).first_or_404()
    
    settlement_type = request.form.get('settlement_type')  # deposit / deduct
    currency = request.form.get('currency')                # YER / SAR / USD
    amount = float(request.form.get('amount', 0.0))
    financial_entity = request.form.get('financial_entity', 'الإدارة المركزية')
    reference_number = request.form.get('reference_number', 'SETTLE-ADMIN-2026')
    notes = request.form.get('notes', '').strip()

    if amount <= 0:
        flash("خطأ محاسبي: لا يمكن إصدار سند تسوية بمبلغ صفر أو سالب.", "danger")
        return redirect(url_for('wallet.display_management_table', search_query=wallet_code))

    currency_attr = currency.lower()  # yer, sar, usd
    current_available = getattr(wallet, f"{currency_attr}_available") or 0.0
    current_total = getattr(wallet, f"{currency_attr}_total") or 0.0

    timestamp = datetime.utcnow().strftime('%M%S')
    generated_settlement_code = f"ST-2026-{currency}-{timestamp}"

    if settlement_type == 'deposit':
        setattr(wallet, f"{currency_attr}_available", current_available + amount)
        setattr(wallet, f"{currency_attr}_total", current_total + amount)
        type_label = "شحن / إضافة رصيد"
        flash_style = "success"

    elif settlement_type == 'deduct':
        if current_available < amount:
            flash(f"فشل إصدار السند: الرصيد المتاح في المحفظة ({current_available:,.2f} {currency}) غير كافٍ لإجراء خصم قيمته {amount:,.2f}.", "danger")
            return redirect(url_for('wallet.display_management_table', search_query=wallet_code))
        
        setattr(wallet, f"{currency_attr}_available", current_available - amount)
        setattr(wallet, f"{currency_attr}_total", max(0.0, current_total - amount))
        type_label = "خصم عكسي"
        flash_style = "inverse"

    new_settlement = AdminSettlement(
        settlement_code=generated_settlement_code,
        wallet_code=wallet.wallet_code,
        settlement_type=type_label,
        amount=amount,
        currency=currency,
        financial_entity=financial_entity,
        reference_number=reference_number,
        reason_notes=notes,
        created_by="المشرف المالي المركزي",
        created_at=datetime.utcnow()
    )

    db.session.add(new_settlement)
    db.session.commit()

    flash(f"تم اعتماد وتعميد سند التسوية الإدارية الموحد رقم ({generated_settlement_code}) بنجاح تام.", flash_style)
    return redirect(url_for('wallet.display_management_table', search_query=wallet_code))
