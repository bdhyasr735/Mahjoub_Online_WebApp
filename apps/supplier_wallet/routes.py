# coding: utf-8
# 📂 apps/supplier_wallet/routes.py

"""
Mahjoub Online - Supplier Wallet Routes
تتضمن كافة المنطق للفلترة ومعالجة حركات الحساب وطلبات السحب اعتماداً على البيانات المسجلة في القاعدة
"""
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction
# استيراد نموذج ملف المورد أو البيانات المسجلة إن وجد
try:
    from apps.models.supplier_db import SupplierProfile
except ImportError:
    SupplierProfile = None

# توحيد اسم الـ Blueprint وتحديد مسار الملفات الثابتة
wallet_bp = Blueprint(
    'supplier_wallet', 
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static'
)

def get_trx_type_attr():
    """التحقق الديناميكي من اسم حقل نوع المعاملة وتجنب الخصائص البرمجية (Properties)"""
    for col_name in ['transaction_type', 'trx_type', 'trans_type']:
        if hasattr(WalletTransaction, col_name):
            attr = getattr(WalletTransaction, col_name)
            if not isinstance(attr, property):
                return attr
    return None

def get_status_attr():
    """التحقق الديناميكي من اسم حقل الحالة وتجنب الخصائص البرمجية (Properties)"""
    for col_name in ['status', 'state']:
        if hasattr(WalletTransaction, col_name):
            attr = getattr(WalletTransaction, col_name)
            if not isinstance(attr, property):
                return attr
    return None

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

def get_registered_supplier_payout_info(supplier_id):
    """جلب بيانات الحساب واسم المالك المسجلة مسبقاً في قاعدة بيانات الموردين"""
    owner_name = ""
    account_details = ""
    
    # 1. محاولة الجلب من جدول SupplierProfile إن وجد
    if SupplierProfile and supplier_id:
        profile = SupplierProfile.query.filter_by(supplier_id=supplier_id).first() or SupplierProfile.query.filter_by(id=supplier_id).first()
        if profile:
            owner_name = getattr(profile, 'owner_name', None) or getattr(profile, 'name', None) or getattr(profile, 'full_name', '')
            account_details = getattr(profile, 'bank_details', None) or getattr(profile, 'account_details', None) or getattr(profile, 'payout_info', '')

    # 2. الجلب من بيانات الحساب الحالي (current_user) إذا لم تتوفر في البروفايل
    if not owner_name and current_user.is_authenticated:
        owner_name = getattr(current_user, 'full_name', None) or getattr(current_user, 'name', None) or getattr(current_user, 'username', '')

    if not account_details and current_user.is_authenticated:
        account_details = getattr(current_user, 'bank_details', None) or getattr(current_user, 'account_details', '')

    return owner_name.strip(), account_details.strip()


@wallet_bp.route('/', methods=['GET'], strict_slashes=False)
@wallet_bp.route('/wallet', methods=['GET'], strict_slashes=False)
@login_required
def wallet():
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    trx_type_col = get_trx_type_attr()
    status_col = get_status_attr()

    if wallet_obj:
        wallet_id = wallet_obj.id
        
        q_completed = db.session.query(db.func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.wallet_id == wallet_id
        )
        if status_col is not None:
            q_completed = q_completed.filter(status_col == 'completed')
        if trx_type_col is not None:
            q_completed = q_completed.filter(trx_type_col.in_(['credit', 'sale_revenue', 'deposit', 'adjustment_credit']))
        completed_credits = q_completed.scalar() or 0.00

        q_pending = db.session.query(db.func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.wallet_id == wallet_id
        )
        if status_col is not None:
            q_pending = q_pending.filter(status_col == 'pending')
        if trx_type_col is not None:
            q_pending = q_pending.filter(trx_type_col.in_(['credit', 'sale_revenue', 'deposit', 'adjustment_credit']))
        pending_credits = q_pending.scalar() or 0.00

        q_withdrawn = db.session.query(db.func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.wallet_id == wallet_id
        )
        if status_col is not None:
            q_withdrawn = q_withdrawn.filter(status_col.in_(['completed', 'pending']))
        if trx_type_col is not None:
            q_withdrawn = q_withdrawn.filter(trx_type_col.in_(['withdrawal', 'debit']))
        total_withdrawn = q_withdrawn.scalar() or 0.00

        avail_bal = getattr(wallet_obj, 'available_balance', None)
        if avail_bal is None:
            avail_bal = float(getattr(wallet_obj, 'balance_sar', 0.00))
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

    page = request.args.get('page', 1, type=int)
    PER_PAGE = 10
    
    query = WalletTransaction.query
    if wallet_obj:
        query = query.filter_by(wallet_id=wallet_obj.id)
    else:
        query = query.filter_by(id=-1)

    trx_type = request.args.get('type', 'all')
    if trx_type != 'all' and trx_type_col is not None:
        query = query.filter(trx_type_col == trx_type)

    status = request.args.get('status', 'all')
    if status != 'all' and status_col is not None:
        query = query.filter(status_col == status)

    search_query = request.args.get('search', '').strip()
    if search_query:
        search_filters = []
        if hasattr(WalletTransaction, 'reference_number'):
            search_filters.append(WalletTransaction.reference_number.ilike(f"%{search_query}%"))
        if hasattr(WalletTransaction, 'voucher_number'):
            search_filters.append(WalletTransaction.voucher_number.ilike(f"%{search_query}%"))
        if hasattr(WalletTransaction, 'description'):
            search_filters.append(WalletTransaction.description.ilike(f"%{search_query}%"))
        if search_filters:
            from sqlalchemy import or_
            query = query.filter(or_(*search_filters))

    from_date_str = request.args.get('from_date', '').strip()
    to_date_str = request.args.get('to_date', '').strip()

    if from_date_str and hasattr(WalletTransaction, 'created_at'):
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
            query = query.filter(WalletTransaction.created_at >= from_date)
        except ValueError:
            pass

    if to_date_str and hasattr(WalletTransaction, 'created_at'):
        try:
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d')
            to_date_end = to_date.replace(hour=23, minute=59, second=59)
            query = query.filter(WalletTransaction.created_at <= to_date_end)
        except ValueError:
            pass

    if hasattr(WalletTransaction, 'created_at'):
        query = query.order_by(WalletTransaction.created_at.desc(), WalletTransaction.id.desc())
    else:
        query = query.order_by(WalletTransaction.id.desc())

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
        pagination=pagination,
        pagination_obj=pagination_obj
    )


@wallet_bp.route('/withdraw', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def withdraw():
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    trx_type_col = get_trx_type_attr()
    status_col = get_status_attr()

    # جلب البيانات المسجلة للمورد من قاعدة البيانات تلقائياً
    registered_owner, registered_details = get_registered_supplier_payout_info(supplier_id)

    if wallet_obj:
        wallet_id = wallet_obj.id

        q_withdrawn = db.session.query(db.func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.wallet_id == wallet_id
        )
        if status_col is not None:
            q_withdrawn = q_withdrawn.filter(status_col.in_(['completed', 'pending']))
        if trx_type_col is not None:
            q_withdrawn = q_withdrawn.filter(trx_type_col.in_(['withdrawal', 'debit']))
        total_withdrawn = q_withdrawn.scalar() or 0.00

        avail_bal = getattr(wallet_obj, 'available_balance', None)
        if avail_bal is None:
            raw_bal = float(getattr(wallet_obj, 'balance_sar', 0.00))
            avail_bal = max(0.00, raw_bal)

        min_withdraw = 50.00
        curr = getattr(wallet_obj, 'currency', 'ر.س')
    else:
        avail_bal = 0.00
        min_withdraw = 50.00
        curr = 'ر.س'

    summary = {
        'available_balance': float(avail_bal),
        'min_withdraw_amount': min_withdraw,
        'currency': curr
    }

    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            method = request.form.get('method', 'bank')

            # الاعتماد التام على البيانات المسجلة في قاعدة البيانات بدلاً من طلبها من النموذج
            owner_name = registered_owner
            account_details = registered_details

            if not wallet_obj:
                flash("تعذر الوصول إلى حساب المحفظة الخاص بك. يرجى إعادة المحاولة.", "danger")
            elif amount < min_withdraw:
                flash(f"الحد الأدنى للسحب هو {min_withdraw:,.2f} {curr}", "danger")
            elif amount > avail_bal:
                flash("المبلغ المطلوب يتجاوز الرصيد المتاح حالياً للسحب!", "danger")
            elif not owner_name:
                flash("اسم المالك غير مسجل في قاعدة البيانات، يرجى تحديث بيانات حسابك أولاً.", "danger")
            else:
                ref_code = f"WDR-{uuid.uuid4().hex[:6].upper()}"
                payout_label = "تحويل بنكي" if method == 'bank' else "شركات التحويل والصرافة"
                
                details_text = f" - التفاصيل: {account_details}" if account_details else " - (مسجل بالسجل الأساسي)"
                
                tx_kwargs = {
                    'wallet_id': wallet_obj.id,
                    'amount': amount,
                    'reference_number': ref_code, 
                    'description': f"طلب سحب عبر {payout_label} | المالك: {owner_name}{details_text}",
                    'created_at': datetime.utcnow()
                }

                if status_col is not None and hasattr(WalletTransaction, 'status'):
                    tx_kwargs['status'] = 'pending'

                if hasattr(WalletTransaction, 'payout_method'):
                    tx_kwargs['payout_method'] = payout_label
                if hasattr(WalletTransaction, 'account_details'):
                    tx_kwargs['account_details'] = account_details or 'مسجل بالنظام'
                if hasattr(WalletTransaction, 'owner_name'):
                    tx_kwargs['owner_name'] = owner_name
                
                if hasattr(WalletTransaction, 'trans_type'):
                    tx_kwargs['trans_type'] = 'withdrawal'
                elif hasattr(WalletTransaction, 'transaction_type'):
                    tx_kwargs['transaction_type'] = 'withdrawal'
                elif hasattr(WalletTransaction, 'trx_type'):
                    tx_kwargs['trx_type'] = 'withdrawal'

                tx = WalletTransaction(**tx_kwargs)
                db.session.add(tx)
                db.session.commit()

                flash("تم تقديم طلب السحب بنجاح بناءً على البيانات المسجلة، وهو قيد المعالجة والتسوية.", "success")
                return redirect(url_for('supplier_wallet.withdraw'))
        except ValueError:
            flash("يرجى إدخال مبلغ مالي صحيح ومقبول.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"حدث خطأ أثناء تقديم الطلب: {str(e)}", "danger")

    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    PER_PAGE = 10

    query = WalletTransaction.query
    if wallet_obj:
        query = query.filter_by(wallet_id=wallet_obj.id)
        if trx_type_col is not None:
            query = query.filter(trx_type_col.in_(['withdrawal', 'debit']))
    else:
        query = query.filter_by(id=-1)

    if status_filter != 'all' and status_col is not None:
        query = query.filter(status_col == status_filter)

    if hasattr(WalletTransaction, 'created_at'):
        query = query.order_by(WalletTransaction.created_at.desc(), WalletTransaction.id.desc())
    else:
        query = query.order_by(WalletTransaction.id.desc())

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
        'supplier_wallet/withdraw.html',
        summary=summary,
        wallet=summary,
        withdrawals=pagination_obj.items,
        active_filter=status_filter,
        pagination_obj=pagination_obj,
        pagination=pagination,
        registered_owner=registered_owner,
        registered_details=registered_details
    )
