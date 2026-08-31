# coding: utf-8
"""
📂 apps/supplier_wallet/routes.py
مسارات واجهات محفظة المورد (Supplier Wallet Routes)
"""

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction, WithdrawalRequest
from apps.models.supplier_db import Supplier
from apps.supplier_wallet.services.wallet_service import WalletService
from apps.supplier_wallet.services.notification_service import NotificationService
from apps.supplier_wallet.utils import get_current_supplier_id, get_trx_type_attr
from decimal import Decimal

wallet_bp = Blueprint('supplier_wallet', __name__, template_folder='templates', url_prefix='/supplier/wallet')


@wallet_bp.route('/')
@login_required
def wallet_dashboard():
    """لوحة تحكم المحفظة الخاصة بالمورد مع معالجة آمنة للأخطاء والتأكد من وجود المحفظة"""
    supplier_id = get_current_supplier_id()
    if not supplier_id:
        NotificationService.notify_error("تعذر تحديد حساب المورد الحالي")
        return redirect(url_for('main.index'))
    
    try:
        # جلب المحفظة أو إنشائها تلقائياً للمورد الحالي
        wallet = WalletService.get_or_create_wallet(db.session, supplier_id, getattr(current_user, 'trade_name', 'متجر المورد'))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        NotificationService.notify_error("حدث خطأ أثناء تحميل بيانات المحفظة")
        return redirect(url_for('main.index'))

    transactions = WalletTransaction.query.filter_by(wallet_id=wallet.id).order_by(WalletTransaction.created_at.desc()).all()
    withdrawal_requests = WithdrawalRequest.query.filter_by(wallet_id=wallet.id).order_by(WithdrawalRequest.created_at.desc()).all()

    return render_template(
        'supplier_wallet/dashboard.html',
        wallet=wallet,
        transactions=transactions,
        withdrawal_requests=withdrawal_requests
    )


@wallet_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    """عرض نموذج السحب (GET) ومعالجة طلب السحب (POST) مع التحقق من الرصيد والبيانات المدخلة بدقة"""
    supplier_id = get_current_supplier_id()
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    if not wallet:
        NotificationService.notify_error("المحفظة غير موجودة")
        return redirect(url_for('supplier_wallet.wallet_dashboard'))

    if request.method == 'POST':
        try:
            raw_amount = request.form.get('amount', '0').strip()
            amount = Decimal(raw_amount) if raw_amount else Decimal('0')
            
            if amount <= 0:
                raise ValueError("مبلغ السحب يجب أن يكون أكبر من الصفر")
                
            if amount > wallet.balance_sar:
                raise ValueError("المبلغ المطلوب يتجاوز رصيد المحفظة المتاح")

            bank_account = request.form.get('bank_account_id', 'مصرف الراجحي - شركة الأناقة للتجارة (SA03 8000 **** **** 4921)')
            notes = request.form.get('notes', '')

            # إنشاء طلب السحب وحفظ التغييرات
            wdr = WalletService.create_withdrawal_request(db.session, wallet.id, bank_account, amount, notes)
            db.session.commit()

            NotificationService.notify_withdrawal_requested(float(amount), wdr.request_number)
            NotificationService.notify_success("تم تقديم طلب السحب بنجاح وهو قيد المراجعة والاعتماد")
            
            # إعادة التوجيه مع تمرير معامل النجاح لإظهار النافذة المنبثقة تلقائياً
            return redirect(url_for('supplier_wallet.withdraw', success='true'))
            
        except ValueError as e:
            db.session.rollback()
            NotificationService.notify_error(str(e))
        except Exception as e:
            db.session.rollback()
            NotificationService.notify_error(f"حدث خطأ غير متوقع أثناء معالجة طلب السحب: {str(e)}")

        return redirect(url_for('supplier_wallet.withdraw'))

    page = request.args.get('page', 1, type=int)
    query = WithdrawalRequest.query.filter_by(wallet_id=wallet.id).order_by(WithdrawalRequest.created_at.desc())
    pagination = query.paginate(page=page, per_page=15, error_out=False)

    active_bank = {
        'bank_name': 'مصرف الراجحي - شركة الأناقة للتجارة (SA03 8000 **** **** 4921)',
        'id': 1
    }

    return render_template(
        'supplier_wallet/withdrawal_form.html',
        wallet=wallet,
        active_bank=active_bank,
        pagination=pagination
    )


@wallet_bp.route('/transactions')
@login_required
def transactions():
    """عرض كشف الحساب وسندات الحركات المالية مع الفلترة الذكية والآمنة"""
    supplier_id = get_current_supplier_id()
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    if not wallet:
        return redirect(url_for('supplier_wallet.wallet_dashboard'))

    query = WalletTransaction.query.filter_by(wallet_id=wallet.id)

    search_query = request.args.get('q', '').strip()
    trans_type = request.args.get('trans_type', '').strip()
    status = request.args.get('status', '').strip()

    if search_query:
        query = query.filter(
            db.or_(
                WalletTransaction.voucher_number.ilike(f'%{search_query}%'),
                WalletTransaction.transfer_number.ilike(f'%{search_query}%'),
                WalletTransaction.reference_number.ilike(f'%{search_query}%'),
                WalletTransaction.description.ilike(f'%{search_query}%')
            )
        )

    trx_column = get_trx_type_attr()
    if trans_type and trx_column is not None:
        query = query.filter(trx_column == trans_type)

    if status and hasattr(WalletTransaction, 'status'):
        query = query.filter_by(status=status)

    transactions = query.order_by(WalletTransaction.created_at.desc()).all()

    return render_template(
        'supplier_wallet/wallet_transactions.html',
        wallet=wallet,
        transactions=transactions
    )


@wallet_bp.route('/store/<string:supplier_code>')
def public_store_view(supplier_code):
    """عرض صفحة متجر المورد العامة بشكل احترافي باستخدام كود المورد الفريد"""
    supplier = Supplier.query.filter_by(supplier_code=supplier_code, status='active').first_or_404()
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
    
    return render_template(
        'supplier_wallet/public_store.html',
        supplier=supplier,
        wallet=wallet
    )
