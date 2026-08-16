# coding: utf-8
from flask import Blueprint, render_template, request, jsonify
from apps.models import SupplierWallet, WalletTransaction, Supplier, db
from sqlalchemy import or_, func
from decimal import Decimal
from datetime import datetime

bp = Blueprint('suppliers_wallets_controller', __name__)

PER_PAGE = 10

@bp.route('/', methods=['GET'])
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '', type=str)
    status_filter = request.args.get('status', 'all', type=str)
    bank_filter = request.args.get('bank', 'all', type=str)

    query = SupplierWallet.query.join(Supplier, Supplier.id == SupplierWallet.supplier_id)

    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            or_(
                SupplierWallet.wallet_code.ilike(search_term),
                Supplier.supplier_code.ilike(search_term),
                Supplier.store_name.ilike(search_term),
                Supplier.trade_name.ilike(search_term),
                Supplier.owner_name.ilike(search_term),
                Supplier.username.ilike(search_term)
            )
        )

    if status_filter and status_filter != 'all':
        query = query.filter(SupplierWallet.status == status_filter)

    if bank_filter and bank_filter != 'all':
        query = query.filter(Supplier.bank_name.ilike(f"%{bank_filter}%"))

    query = query.order_by(SupplierWallet.id.desc())

    total_sar_balance = db.session.query(func.sum(SupplierWallet.balance_sar)).scalar() or Decimal('0.00')
    total_pending_balance = db.session.query(func.sum(SupplierWallet.balance_pending)).scalar() or Decimal('0.00')
    pending_withdrawals_amount = db.session.query(func.sum(WalletTransaction.amount)).filter_by(status='pending').scalar() or Decimal('0.00')
    total_wallets_balance = Decimal(str(total_sar_balance)) + Decimal(str(total_pending_balance))

    kpis = {
        'total_wallets_balance': total_wallets_balance,
        'total_available_payouts': total_sar_balance,
        'total_escrow_held': total_pending_balance,
        'total_suppliers_count': SupplierWallet.query.count(),
        'active_suppliers_count': SupplierWallet.query.filter_by(status='active').count(),
        'pending_withdrawals_amount': pending_withdrawals_amount,
        'pending_withdrawals_count': WalletTransaction.query.filter_by(status='pending').count()
    }

    pagination_obj = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    suppliers = pagination_obj.items

    pagination = {
        'current_page': pagination_obj.page,
        'total_pages': pagination_obj.pages,
        'has_prev': pagination_obj.has_prev,
        'has_next': pagination_obj.has_next,
        'total_count': pagination_obj.total,
        'per_page': PER_PAGE,
        'prev_num': pagination_obj.prev_num,
        'next_num': pagination_obj.next_num,
    }

    return render_template(
        'admin/suppliers_wallets.html',
        kpis=kpis,
        pagination=pagination,
        suppliers=suppliers,
        search_query=search_query,
        status_filter=status_filter,
        bank_filter=bank_filter
    )


@bp.route('/<int:supplier_id>', methods=['GET'])
def supplier_ledger_detail(supplier_id):
    wallet = SupplierWallet.query.get_or_404(supplier_id)
    transactions = WalletTransaction.query.filter_by(wallet_id=wallet.id).order_by(WalletTransaction.created_at.desc()).all()
    return render_template(
        'admin/supplier_ledger_detail.html',
        wallet=wallet,
        transactions=transactions
    )


# ==========================================================
# ✅ 1. مسار POST: تجميد محفظة المورد
# ==========================================================
@bp.route('/<int:supplier_id>/freeze', methods=['POST'])
def freeze_supplier_wallet(supplier_id):
    try:
        # جلب البيانات المرسلة من المودال (JSON)
        data = request.get_json()
        reason = data.get('reason', 'تم التجميد بواسطة المسؤول')

        # البحث عن المحفظة
        wallet = SupplierWallet.query.get_or_404(supplier_id)

        # التحقق من أنها ليست مجمدة بالفعل
        if wallet.status == 'frozen':
            return jsonify({'success': False, 'message': 'هذه المحفظة مجمدة بالفعل.'})

        # تنفيذ التجميد
        wallet.status = 'frozen'
        wallet.updated_at = datetime.utcnow()

        # حفظ التغيير
        db.session.commit()

        return jsonify({
            'success': True, 
            'message': f'تم تجميد محفظة المورد بنجاح.',
            'new_status': 'frozen'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء التجميد: {str(e)}'})


# ==========================================================
# ✅ 2. مسار POST: تغذية محفظة المورد (إيداع/خصم مالي)
# ==========================================================
@bp.route('/<int:supplier_id>/fund', methods=['POST'])
def fund_supplier_wallet(supplier_id):
    try:
        data = request.get_json()
        trans_type = data.get('trans_type') # 'deposit' أو 'withdraw'
        amount = Decimal(str(data.get('amount', 0)))
        currency = data.get('currency', 'SAR')
        description = data.get('reason', 'تغذية محفظة يدوية')

        # التحقق من صحة المبلغ
        if amount <= 0:
            return jsonify({'success': False, 'message': 'يجب أن يكون المبلغ أكبر من 0.'})

        # البحث عن المحفظة
        wallet = SupplierWallet.query.get_or_404(supplier_id)

        # التأكد من أن المحفظة نشطة (لا يمكن إيداعها إذا كانت مجمدة)
        if wallet.status == 'frozen':
            return jsonify({'success': False, 'message': 'لا يمكن إجراء حركات مالية على محفظة مجمدة.'})

        current_balance = Decimal(str(wallet.balance_sar))
        
        # حساب الرصيد الجديد
        if trans_type == 'deposit':
            new_balance = current_balance + amount
        elif trans_type == 'withdraw':
            if amount > current_balance:
                return jsonify({'success': False, 'message': 'الرصيد غير كافٍ لإجراء هذا الخصم.'})
            new_balance = current_balance - amount
        else:
            return jsonify({'success': False, 'message': 'نوع القيد غير معروف.'})

        # إنشاء سجل حركة مالية (WalletTransaction) في قاعدة البيانات
        new_transaction = WalletTransaction(
            wallet_id=wallet.id,
            trans_type=trans_type,
            status='completed',
            amount=amount,
            currency=currency,
            balance_before=current_balance,
            balance_after=new_balance
        )
        # استخدام التشفير الموجود في الموديل الخاص بك (description)
        new_transaction.description = description 
        
        db.session.add(new_transaction)

        # تحديث رصيد المحفظة
        wallet.balance_sar = new_balance
        wallet.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'تم تنفيذ القيد المالي بنجاح.',
            'new_balance': float(new_balance)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء التغذية: {str(e)}'})
