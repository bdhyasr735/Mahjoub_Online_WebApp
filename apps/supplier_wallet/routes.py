# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction, WithdrawalRequest
from apps.models.supplier_db import Supplier
from apps.supplier_wallet.services.wallet_service import WalletService
from apps.supplier_wallet.services.notification_service import NotificationService
from apps.supplier_wallet.utils import get_current_supplier_id, get_trx_type_attr
import re
import traceback
from decimal import Decimal
from datetime import datetime

# ✅ تعريف الـ Blueprint بنفس اسم الـ LINKS في registry.py
wallet_bp = Blueprint('supplier_wallet', __name__, template_folder='templates', url_prefix='/supplier/wallet')


# ============================================
# دالة مساعدة للحصول على رصيد المحفظة بأمان
# ============================================
def get_wallet_balance(wallet):
    """الحصول على رصيد المحفظة بغض النظر عن اسم العمود"""
    if not wallet:
        return Decimal('0.0')
    
    # قائمة بأسماء الأعمدة المحتملة للرصيد
    if hasattr(wallet, 'balance'):
        return Decimal(str(wallet.balance or 0.0))
    elif hasattr(wallet, 'balance_sar'):
        return Decimal(str(wallet.balance_sar or 0.0))
    elif hasattr(wallet, 'wallet_balance'):
        return Decimal(str(wallet.wallet_balance or 0.0))
    elif hasattr(wallet, 'amount'):
        return Decimal(str(wallet.amount or 0.0))
    else:
        print(f"⚠️ [تحذير]: لم يتم العثور على عمود الرصيد في SupplierWallet")
        return Decimal('0.0')


def get_sidebar_modules():
    """دالة مساعدة لجلب الموديولات والقوائم الجانبية الخاصة بلوحة تحكم المورد"""
    supplier_modules = {}
    
    # محاولة جلب الموديولات من السجل الرئيسي
    try:
        from apps.suppliers_dashboard.registry import MODULES_REGISTRY
        if MODULES_REGISTRY:
            supplier_modules = MODULES_REGISTRY.copy()
    except ImportError:
        pass
    
    # محاولة جلب الموديولات من current_app
    if not supplier_modules and hasattr(current_app, 'supplier_modules') and current_app.supplier_modules:
        supplier_modules = current_app.supplier_modules.copy()
    
    # ✅ القائمة الاحتياطية الكاملة (جميع الموديولات)
    if not supplier_modules:
        supplier_modules = {
            'suppliers_dashboard': {
                'title': 'الرئيسية',
                'icon': 'fas fa-chart-pie',
                'links': {
                    'suppliers_dashboard.index': 'الرئيسية'
                }
            },
            'supplier_products': {
                'title': 'إدارة المنتجات',
                'icon': 'fas fa-box',
                'links': {
                    'supplier_products.index': 'جميع المنتجات',
                    'supplier_products.add': 'إضافة منتج جديد'
                }
            },
            'supplier_orders': {
                'title': 'المبيعات والطلبات',
                'icon': 'fas fa-shopping-cart',
                'links': {
                    'supplier_orders.index': 'الطلبات الواردة',
                    'supplier_orders.history': 'سجل المبيعات'
                }
            },
            'supplier_wallet': {
                'title': 'الإدارة المالية',
                'icon': 'fas fa-wallet',
                'links': {
                    'supplier_wallet.wallet_dashboard': 'المحفظة والسحب',
                    'supplier_wallet.transactions': 'حركة المحفظة',
                    'supplier_wallet.withdraw': 'سحب الرصيد'
                }
            },
            'supplier_staff': {
                'title': 'الموظفين',
                'icon': 'fas fa-users',
                'links': {
                    'supplier_staff.index': 'قائمة الموظفين',
                    'supplier_staff.add': 'إضافة موظف'
                }
            }
        }
    
    return supplier_modules


def get_current_wallet_identifier():
    supplier_id = get_current_supplier_id()
    
    # إذا لم يتم العثور على supplier_id بالطريقة المعتادة، نأخذ معرف المستخدم الحالي
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id
        
    if not supplier_id:
        return '1'  # معرف افتراضي آمن يمنع ظهور كلمة general
    
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if wallet:
        if hasattr(wallet, 'wallet_code') and wallet.wallet_code:
            return str(wallet.wallet_code)
        return str(wallet.id)
        
    trade_name = getattr(current_user, 'trade_name', None)
    if trade_name:
        slug = re.sub(r'[^\w\s-]', '', trade_name).strip().lower()
        slug = re.sub(r'[-\s]+', '-', slug)
        if slug:
            return slug
            
    return str(supplier_id)


# ============================================
# مسارات إعادة التوجيه بدون wallet_id (للقائمة الجانبية)
# ============================================
@wallet_bp.route('/transactions')
@login_required
def transactions_redirect():
    """إعادة توجيه إلى حركة المحفظة مع wallet_id الفعلي"""
    wallet_id = get_current_wallet_identifier()
    return redirect(url_for('supplier_wallet.transactions', wallet_id=wallet_id))


@wallet_bp.route('/withdraw')
@login_required
def withdraw_redirect():
    """إعادة توجيه إلى سحب الرصيد مع wallet_id الفعلي"""
    wallet_id = get_current_wallet_identifier()
    return redirect(url_for('supplier_wallet.withdraw', wallet_id=wallet_id))


# ============================================
# المسارات الرئيسية
# ============================================
@wallet_bp.route('/')
@wallet_bp.route('/dashboard')
@login_required
def wallet_dashboard_redirect():
    wallet_id = get_current_wallet_identifier()
    return redirect(url_for('supplier_wallet.wallet_dashboard', wallet_id=wallet_id))


@wallet_bp.route('/<string:wallet_id>/')
@wallet_bp.route('/<string:wallet_id>/dashboard')
@login_required
def wallet_dashboard(wallet_id):
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id
        
    if not supplier_id:
        return redirect(url_for('main.index'))
    
    try:
        wallet = WalletService.get_or_create_wallet(db.session, supplier_id, getattr(current_user, 'trade_name', 'متجر المورد'))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [Wallet Dashboard Error]: {str(e)}")
        traceback.print_exc()
        return redirect(url_for('main.index'))

    transactions = WalletTransaction.query.filter_by(wallet_id=wallet.id).order_by(WalletTransaction.created_at.desc()).all()
    withdrawal_requests = WithdrawalRequest.query.filter_by(wallet_id=wallet.id).order_by(WithdrawalRequest.created_at.desc()).all()

    modules = get_sidebar_modules()

    return render_template(
        'supplier_wallet/dashboard.html',
        wallet=wallet,
        transactions=transactions,
        withdrawal_requests=withdrawal_requests,
        supplier_modules=modules,
        modules_registry=modules
    )


@wallet_bp.route('/<string:wallet_id>/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw(wallet_id):
    """عرض نموذج السحب ومعالجته"""
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id
        
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    if not wallet:
        return redirect(url_for('supplier_wallet.wallet_dashboard', wallet_id=wallet_id))

    # ✅ الحصول على الرصيد الحالي بأمان
    current_balance = get_wallet_balance(wallet)

    if request.method == 'POST':
        try:
            raw_amount = request.form.get('amount', '0').strip().replace(',', '.')
            amount = Decimal(raw_amount) if raw_amount else Decimal('0')
            
            if amount <= 0:
                raise ValueError("مبلغ السحب يجب أن يكون أكبر من الصفر")
                
            # ✅ استخدام current_balance بدلاً من wallet.balance_sar
            if amount > current_balance:
                raise ValueError("المبلغ المطلوب يتجاوز رصيد المحفظة المتاح")

            bank_account = request.form.get('bank_account_id', 'مصرف الراجحي - شركة الأناقة للتجارة')
            notes = request.form.get('notes', '')

            wdr = WalletService.create_withdrawal_request(db.session, wallet.id, bank_account, amount, notes)
            db.session.commit()

            return redirect(url_for('supplier_wallet.withdraw', wallet_id=wallet_id, success='true'))
            
        except ValueError as e:
            db.session.rollback()
            print(f"⚠️ [Withdrawal ValueError]: {str(e)}")
            flash(str(e), "danger")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Withdrawal Exception]: {str(e)}")
            traceback.print_exc()
            flash(f"حدث خطأ: {str(e)}", "danger")

        return redirect(url_for('supplier_wallet.withdraw', wallet_id=wallet_id))

    page = request.args.get('page', 1, type=int)
    query = WithdrawalRequest.query.filter_by(wallet_id=wallet.id).order_by(WithdrawalRequest.created_at.desc())
    pagination = query.paginate(page=page, per_page=15, error_out=False)

    active_bank = {
        'bank_name': 'مصرف الراجحي - شركة الأناقة للتجارة',
        'id': 1
    }

    modules = get_sidebar_modules()

    return render_template(
        'supplier_wallet/withdrawal_form.html',
        wallet=wallet,
        balance=current_balance,  # ✅ تمرير الرصيد إلى القالب
        active_bank=active_bank,
        pagination=pagination,
        supplier_modules=modules,
        modules_registry=modules
    )


@wallet_bp.route('/receipt/<string:request_number>')
@login_required
def withdrawal_receipt(request_number):
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id
        
    if not supplier_id:
        return redirect(url_for('main.index'))

    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if not wallet:
        return redirect(url_for('main.index'))

    receipt = WithdrawalRequest.query.filter_by(request_number=request_number, wallet_id=wallet.id).first_or_404()
    supplier = Supplier.query.get(supplier_id)
    modules = get_sidebar_modules()

    return render_template(
        'supplier_wallet/withdrawal_receipt.html',
        receipt=receipt,
        wallet=wallet,
        supplier=supplier,
        supplier_modules=modules,
        modules_registry=modules
    )


@wallet_bp.route('/<string:wallet_id>/transactions')
@login_required
def transactions(wallet_id):
    """عرض كشف الحساب"""
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id
        
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    if not wallet:
        return redirect(url_for('supplier_wallet.wallet_dashboard', wallet_id=wallet_id))

    # جلب الحركات المالية
    transactions_list = WalletTransaction.query.filter_by(wallet_id=wallet.id).all()
    
    # جلب طلبات السحب
    withdrawal_requests = WithdrawalRequest.query.filter_by(wallet_id=wallet.id).all()
    
    # دمج القائمتين
    all_transactions = list(transactions_list)
    
    for req in withdrawal_requests:
        all_transactions.append({
            'voucher_number': req.request_number,
            'reference_number': req.request_number,
            'transaction_type': 'debit',
            'amount': req.amount,
            'balance_after': None,
            'status': req.status,
            'created_at': req.created_at,
            'is_withdrawal': True
        })
    
    # ترتيب حسب التاريخ (الأحدث أولاً)
    all_transactions.sort(key=lambda x: x.get('created_at') or x.created_at, reverse=True)

    # فلترة حسب البحث
    search_query = request.args.get('q', '').strip()
    trans_type = request.args.get('trans_type', '').strip()
    status = request.args.get('status', '').strip()

    if search_query:
        all_transactions = [
            t for t in all_transactions
            if search_query.lower() in str(t.get('voucher_number', '')).lower()
            or search_query.lower() in str(t.get('reference_number', '')).lower()
        ]

    if trans_type:
        all_transactions = [
            t for t in all_transactions
            if t.get('transaction_type') == trans_type
        ]

    if status:
        all_transactions = [
            t for t in all_transactions
            if t.get('status') == status
        ]

    balance = get_wallet_balance(wallet)
    modules = get_sidebar_modules()

    return render_template(
        'supplier_wallet/wallet_transactions.html',
        wallet=wallet,
        balance=balance,
        transactions=all_transactions,
        supplier_modules=modules,
        modules_registry=modules,
        now=datetime.now()
    )


@wallet_bp.route('/store/<string:supplier_code>')
def public_store_view(supplier_code):
    supplier = Supplier.query.filter_by(supplier_code=supplier_code, status='active').first_or_404()
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
    modules = get_sidebar_modules()
    
    return render_template(
        'supplier_wallet/public_store.html',
        supplier=supplier,
        wallet=wallet,
        supplier_modules=modules,
        modules_registry=modules
    )
