from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from apps.models import Wallet, WithdrawalRequest, Transaction
from datetime import datetime

wallet_bp = Blueprint('wallet', __name__, url_prefix='/wallet')

@wallet_bp.route('/overview', methods=['GET'])
@login_required
def overview():
    """
    نافذة مركز الرقابة والتسويات المادية
    تعرض إحصائيات النظام الشاملة، وبطاقات المحافظ الثلاثية للمورد المستدعى،
    إلى جانب طلبات السحب الجارية بانتظار التعميد.
    """
    # 1. حساب إحصائيات النظام الإجمالية لعام 2026
    total_wallets_count = Wallet.query.count()
    total_yer_system = db.session.query(db.func.sum(Wallet.yer_available)).scalar() or 0.0
    total_sar_system = db.session.query(db.func.sum(Wallet.sar_available)).scalar() or 0.0
    total_usd_system = db.session.query(db.func.sum(Wallet.usd_available)).scalar() or 0.0

    search_query = request.args.get('search_query', '').strip()
    wallet = None

    # 2. استدعاء بيانات المحفظة والهوية عند البحث
    if search_query:
        wallet = Wallet.query.filter(
            (Wallet.supplier_id == search_query) |
            (Wallet.supplier_name.like(f"%{search_query}%")) |
            (Wallet.wallet_code == search_query) |
            (Wallet.business_entity.like(f"%{search_query}%"))
        ).first()
        
        if not wallet:
            flash('لم يتم العثور على أي كيان تجاري أو محفظة مطابقة للبحث.', 'warning')

    # 3. جلب طلبات السحب النقدية المعلقة فقط للتعميد الفوري
    withdrawal_requests = WithdrawalRequest.query.filter_by(status='pending').order_by(WithdrawalRequest.created_at.desc()).all()

    return render_template(
        'admin/wallet_overview.html',
        wallet=wallet,
        current_search=search_query,
        total_wallets_count=total_wallets_count,
        total_yer_system=total_yer_system,
        total_sar_system=total_sar_system,
        total_usd_system=total_usd_system,
        withdrawal_requests=withdrawal_requests
    )


@wallet_bp.route('/statements/<string:supplier_id>', methods=['GET'])
@login_required
def statements(supplier_id):
    """
    النافذة المستقلة الخاصة بكشوفات الحسابات والعمليات التفصيلية
    بناءً على التحديث الحوكمي لمنع تكدس البيانات في واجهة الرقابة.
    """
    wallet = Wallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    
    # جلب السجل الكامل للحركة المالية (كشف الحساب التاريخي)
    transactions = Transaction.query.filter_by(wallet_code=wallet.wallet_code).order_by(Transaction.created_at.desc()).all()
    
    return render_template(
        'admin/account_statements.html',
        wallet=wallet,
        transactions=transactions
    )


@wallet_bp.route('/withdrawal/<int:request_id>/<string:action>', methods=['POST'])
@login_required
def handle_withdrawal(request_id, action):
    """
    مراجعة وتعميد طلبات السحب النقدي المباشر من واجهة الإدارة المركزية
    """
    req = WithdrawalRequest.query.get_or_404(request_id)
    wallet = Wallet.query.filter_by(wallet_code=req.wallet_code).first_or_404()
    
    currency_attr = req.currency.lower()  # yer, sar, usd

    if action == 'approve':
        # تعميد الصرف ونقل المبالغ من المعلق إلى المسحوبات الفندقية الفعالة
        pending_balance = getattr(wallet, f"{currency_attr}_pending", 0.0)
        withdrawn_balance = getattr(wallet, f"{currency_attr}_withdrawn", 0.0)
        
        if pending_balance >= req.amount:
            setattr(wallet, f"{currency_attr}_pending", pending_balance - req.amount)
            setattr(wallet, f"{currency_attr}_withdrawn", withdrawn_balance + req.amount)
            req.status = 'approved'
            req.processed_at = datetime.utcnow()
            
            # تسجيل عملية الخصم النهائي في جدول العمليات
            new_tx = Transaction(
                wallet_code=wallet.wallet_code,
                tx_type='withdrawal',
                currency=req.currency,
                amount=req.amount,
                description=f"تعميد سحب نقدي عبر {req.payout_method} - تفاصيل الحوالة: {req.payout_details}"
            )
            db.session.add(new_tx)
            db.session.commit()
            flash('تم تعميد طلب السحب وصرف المبالغ بنجاح لتحديث الحساب.', 'success')
        else:
            flash('خطأ حوكمي: الرصيد المعلق لا يكفي لإتمام هذه العملية.', 'danger')

    elif action == 'reject':
        # رفض الطلب وإعادة الأموال المعلقة إلى الرصيد المتاح فوراً
        pending_balance = getattr(wallet, f"{currency_attr}_pending", 0.0)
        available_balance = getattr(wallet, f"{currency_attr}_available", 0.0)
        
        if pending_balance >= req.amount:
            setattr(wallet, f"{currency_attr}_pending", pending_balance - req.amount)
            setattr(wallet, f"{currency_attr}_available", available_balance + req.amount)
            req.status = 'rejected'
            req.processed_at = datetime.utcnow()
            db.session.commit()
            flash('تم رفض طلب السحب وإعادة المبالغ المحجوزة إلى الرصيد المتاح بنجاح.', 'info')
            
    return redirect(url_for('wallet.overview', search_query=wallet.supplier_id))


@wallet_bp.route('/admin-settlement/<string:wallet_code>', methods=['POST'])
@login_required
def admin_settlement(wallet_code):
    """
    إجراء تسوية حسابية إدارية استثنائية (إيداع أو سحب إداري معتمد بالبيان)
    """
    wallet = Wallet.query.filter_by(wallet_code=wallet_code).first_or_404()
    
    settlement_type = request.form.get('settlement_type')
    currency = request.form.get('currency')  # YER, SAR, USD
    amount = float(request.form.get('amount', 0))
    notes = request.form.get('notes', '').strip()
    
    currency_attr = currency.lower()
    available_balance = getattr(wallet, f"{currency_attr}_available", 0.0)
    total_balance = getattr(wallet, f"{currency_attr}_total", 0.0)
    
    if settlement_type == 'deposit':
        # شحن يدوي وإضافة رصيد
        setattr(wallet, f"{currency_attr}_available", available_balance + amount)
        setattr(wallet, f"{currency_attr}_total", total_balance + amount)
        flash_msg = f"تم إيداع مبلغ {amount} {currency} بنجاح كشحن إداري موثق."
        tx_type = 'deposit'
    
    elif settlement_type == 'deduct':
        # تسوية عكسية وخصم مادي
        if available_balance >= amount:
            setattr(wallet, f"{currency_attr}_available", available_balance - amount)
            setattr(wallet, f"{currency_attr}_total", total_balance - amount)
            flash_msg = f"تم خصم مبلغ {amount} {currency} بنجاح بناءً على التسوية الإدارية."
            tx_type = 'deduction'
        else:
            flash('فشلت التسوية العكسية: الرصيد الحالي المتاح للمورد غير كافٍ لإجراء الخصم.', 'danger')
            return redirect(url_for('wallet.overview', search_query=wallet.supplier_id))
            
    # توثيق الحركة في قاعدة البيانات ليظهر فوراً في كشوفات الحسابات
    settlement_tx = Transaction(
        wallet_code=wallet.wallet_code,
        tx_type=tx_type,
        currency=currency,
        amount=amount,
        description=f"تسوية إدارية معتمدة: {notes}"
    )
    db.session.add(settlement_tx)
    db.session.commit()
    
    flash(flash_msg, 'success')
    return redirect(url_for('wallet.overview', search_query=wallet.supplier_id))
