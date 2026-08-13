"""
Mahjoub Online - Supplier Wallet Routes
تتضمن كافة المنطق للفلترة ومعالجة حركات الحساب وطلبات السحب المباشرة من قاعدة البيانات
"""
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.supplier_db import Supplier

# توحيد اسم الـ Blueprint وتحديد مسار الملفات الثابتة
wallet_bp = Blueprint(
    'supplier_wallet', 
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static'
)

def get_current_supplier_id():
    """استخراج رقم المورد الحالي سواء كان هو التاجر أو موظف لدى المورد"""
    if not current_user.is_authenticated:
        return None
    user_type = session.get('user_type')
    if user_type == 'supplier':
        return getattr(current_user, 'id', None)
    elif user_type == 'staff':
        return getattr(current_user, 'supplier_id', None)
    return getattr(current_user, 'supplier_id', getattr(current_user, 'id', None))

def get_or_create_supplier_wallet(supplier_id):
    """جلب محفظة المورد أو إنشائها تلقائياً في حال عدم وجودها"""
    if not supplier_id:
        return None
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if not wallet:
        try:
            wallet = SupplierWallet(
                supplier_id=supplier_id,
                wallet_code=f"MAH-WEL{uuid.uuid4().hex[:6].upper()}{supplier_id}",
                balance_sar=0.00
            )
            db.session.add(wallet)
            db.session.commit()
        except Exception:
            db.session.rollback()
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    return wallet


@wallet_bp.route('/', methods=['GET'])
@wallet_bp.route('/wallet', methods=['GET'])
@login_required
def wallet():
    """
    نافذة المحفظة (كشف الحساب العام):
    مخصصة لعرض الأرصدة الإجمالية وجدولة الحركات المالية الفعلية من قاعدة البيانات مع الترقيم والفلترة.
    """
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)

    # حساب الأرصدة الفعلية ديناميكياً
    if wallet_obj:
        wallet_id = wallet_obj.id
        
        # الأرباح المكتملة المعلقة أو المعالجة
        completed_credits = db.session.query(db.func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.wallet_id == wallet_id,
            WalletTransaction.transaction_type == 'credit',
            WalletTransaction.status == 'completed'
        ).scalar() or 0.00

        pending_credits = db.session.query(db.func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.wallet_id == wallet_id,
            WalletTransaction.transaction_type == 'credit',
            WalletTransaction.status == 'pending'
        ).scalar() or 0.00

        total_withdrawn = db.session.query(db.func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.wallet_id == wallet_id,
            WalletTransaction.transaction_type.in_(['withdrawal', 'debit']),
            WalletTransaction.status == 'completed'
        ).scalar() or 0.00

        # حساب الرصيد المتاح بمرونة
        avail_bal = getattr(wallet_obj, 'available_balance', None)
        if avail_bal is none:
            avail_bal = float(getattr(wallet_obj, 'balance_sar', 0.00)) - float(total_withdrawn)
            avail_bal = max(0.00, avail_bal)

        tot_bal = avail_bal + float(pending_credits)

        summary = {
            'total_balance': float(tot_bal),
            'available_balance': float(avail_bal),
            'pending_balance': float(pending_credits),
            'total_withdrawn': float(total_withdrawn),
            'currency': getattr(wallet_obj, 'currency', 'ر.س')
        }
    else:
        summary = {
            'total_balance': 0.00,
            'available_balance': 0.00,
            'pending_balance': 0.00,
            'total_withdrawn': 0.00,
            'currency': 'ر.س'
        }

    # الفلترة والبحث من قاعدة البيانات مباشرة
    page = request.args.get('page', 1, type=int)
    PER_PAGE = 10
    
    query = WalletTransaction.query
    if wallet_obj:
        query = query.filter_by(wallet_id=wallet_obj.id)
    else:
        query = query.filter_by(id=-1)  # نتيجة فارغة إذا لم تتوفر محفظة

    trx_type = request.args.get('type', 'all')
    if trx_type != 'all':
        query = query.filter(WalletTransaction.transaction_type == trx_type)

    status = request.args.get('status', 'all')
    if status != 'all':
        query = query.filter(WalletTransaction.status == status)

    search_query = request.args.get('search', '').strip()
    if search_query:
        query = query.filter(
            (WalletTransaction.reference_code.ilike(f"%{search_query}%")) |
            (WalletTransaction.description.ilike(f"%{search_query}%"))
        )

    # الترتيب حسب الأحدث
    query = query.order_by(WalletTransaction.created_at.desc(), WalletTransaction.id.desc())

    # الترقيم (Pagination)
    pagination_obj = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    pagination = {
        'items': pagination_obj.items,
        'page': pagination_obj.page,
        'total_pages': pagination_obj.pages,
        'total_items': pagination_obj.total,
        'has_prev': pagination_obj.has_prev,
        'has_next': pagination_obj.has_next,
        'per_page': PER_PAGE
    }

    return render_template(
        'supplier_wallet/wallet.html',
        summary=summary,
        wallet=summary,
        pagination=pagination
    )


@wallet_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    """
    نافذة طلب السحب المستقلة:
    مخصصة كلياً لتقديم ومتابعة طلبات سحب الأرباح والمدفوعات الفعيلة للتاجر من قاعدة البيانات.
    """
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)

    # حساب الرصيد المتاح الفعلي من قاعدة البيانات
    if wallet_obj:
        wallet_id = wallet_obj.id

        total_withdrawn = db.session.query(db.func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.wallet_id == wallet_id,
            WalletTransaction.transaction_type.in_(['withdrawal', 'debit']),
            WalletTransaction.status.in_(['completed', 'pending'])
        ).scalar() or 0.00

        avail_bal = getattr(wallet_obj, 'available_balance', None)
        if avail_bal is None:
            raw_bal = float(getattr(wallet_obj, 'balance_sar', 0.00))
            avail_bal = max(0.00, raw_bal - float(total_withdrawn))

        min_withdraw = 500.00
        curr = getattr(wallet_obj, 'currency', 'ر.س')
    else:
        avail_bal = 0.00
        min_withdraw = 500.00
        curr = 'ر.س'

    summary = {
        'available_balance': float(avail_bal),
        'min_withdraw_amount': min_withdraw,
        'currency': curr
    }

    # معالجة تقديم طلب سحب جديد (POST)
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            method = request.form.get('method', 'bank')
            account_details = request.form.get('account_details', '').strip()

            if not wallet_obj:
                flash("تعذر الوصول إلى حساب المحفظة الخاص بك. يرجى إعادة المحاولة.", "danger")
            elif amount < min_withdraw:
                flash(f"الحد الأدنى للسحب هو {min_withdraw:,.2f} {curr}", "danger")
            elif amount > avail_bal:
                flash("المبلغ المطلوب يتجاوز الرصيد المتاح حالياً للسحب!", "danger")
            elif not account_details:
                flash("يرجى إدخال تفاصيل الحساب البنكي أو شركة الصرافة بشكل صحيح.", "danger")
            else:
                # إنشاء معاملة سحب جديدة في قاعدة البيانات
                ref_code = f"WDR-{uuid.uuid4().hex[:6].upper()}"
                payout_label = "تحويل بنكي" if method == 'bank' else "شركات التحويل والصرافة"
                
                tx = WalletTransaction(
                    wallet_id=wallet_obj.id,
                    amount=amount,
                    transaction_type='withdrawal',
                    payout_method=payout_label,
                    account_details=account_details,
                    status='pending',
                    reference_code=ref_code,
                    description=f"طلب سحب أرباح عبر {payout_label} ({account_details[:30]}...)",
                    created_at=datetime.utcnow()
                )

                db.session.add(tx)
                db.session.commit()

                flash("تم تقديم طلب السحب بنجاح، وهو قيد المعالجة المالي والتسوية خلال 24-48 ساعة.", "success")
                return redirect(url_for('supplier_wallet.withdraw'))
        except ValueError:
            flash("يرجى إدخال مبلغ مالي صحيح ومقبول.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"حدث خطأ أثناء تقديم الطلب: {str(e)}", "danger")

    # تصفية وجلب سجل طلبات السحب السابقة (GET)
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    PER_PAGE = 10

    query = WalletTransaction.query
    if wallet_obj:
        query = query.filter_by(wallet_id=wallet_obj.id)
        query = query.filter(WalletTransaction.transaction_type.in_(['withdrawal', 'debit']))
    else:
        query = query.filter_by(id=-1)

    if status_filter != 'all':
        query = query.filter(WalletTransaction.status == status_filter)

    query = query.order_by(WalletTransaction.created_at.desc(), WalletTransaction.id.desc())
    
    pagination_obj = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template(
        'supplier_wallet/withdraw.html',
        summary=summary,
        wallet=summary,
        withdrawals=pagination_obj.items,
        active_filter=status_filter,
        pagination_obj=pagination_obj
    )