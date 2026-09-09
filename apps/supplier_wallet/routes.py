# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/routes.py

import re
import traceback
import importlib
from decimal import Decimal
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from werkzeug.routing import BuildError

from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction, WithdrawalRequest
from apps.models.supplier_db import Supplier
from apps.supplier_wallet.services.wallet_service import WalletService
from apps.supplier_wallet.services.notification_service import NotificationService
from apps.supplier_wallet.utils import get_current_supplier_id, get_trx_type_attr

supplier_wallet_bp = Blueprint('supplier_wallet_bp', __name__, template_folder='templates', url_prefix='/supplier/wallet')


def safe_redirect_home():
    """إعادة توجيه آمنة عند الفشل لتجنب خطأ BuildError."""
    try:
        return redirect(url_for('main.index'))
    except BuildError:
        try:
            return redirect(url_for('suppliers_dashboard.index'))
        except BuildError:
            return redirect('/')


def get_wallet_balance(wallet):
    """جلب رصيد المحفظة الإجمالي."""
    if not wallet:
        return Decimal('0.0')
    if hasattr(wallet, 'balance') and wallet.balance is not None:
        return Decimal(str(wallet.balance))
    elif hasattr(wallet, 'balance_sar') and wallet.balance_sar is not None:
        return Decimal(str(wallet.balance_sar))
    elif hasattr(wallet, 'wallet_balance') and wallet.wallet_balance is not None:
        return Decimal(str(wallet.wallet_balance))
    elif hasattr(wallet, 'amount') and wallet.amount is not None:
        return Decimal(str(wallet.amount))
    else:
        return Decimal('0.0')


def get_sidebar_modules():
    """تجميع موديولات القائمة الجانبية للمورد ديناميكياً لتشمل جميع الموديولات المتاحة."""
    supplier_modules = {}

    # 1️⃣ محاولة جلب الموديولات من السجل المركزي للداشبورد إن وجد
    try:
        from apps.suppliers_dashboard.registry import MODULES_REGISTRY
        if MODULES_REGISTRY:
            supplier_modules.update(MODULES_REGISTRY)
    except ImportError:
        pass

    # 2️⃣ محاولة جلب الموديولات الممررة على مستوى التطبيق (current_app)
    if hasattr(current_app, 'supplier_modules') and current_app.supplier_modules:
        supplier_modules.update(current_app.supplier_modules)

    # 3️⃣ المسح الديناميكي على كافة سجلات الموديولات (Registries) المسجلة في التطبيق
    registry_paths = [
        'apps.suppliers_dashboard.registry',
        'apps.supplier_products.registry',
        'apps.supplier_orders.registry',
        'apps.supplier_wallet.registry',
        'apps.suppliers_permissions.registry'
    ]

    for path in registry_paths:
        try:
            mod = importlib.import_module(path)
            if hasattr(mod, 'get_nav_metadata'):
                metadata = mod.get_nav_metadata()
                if metadata.get('show_in_supplier', True):
                    supplier_modules[metadata['key']] = metadata
            elif hasattr(mod, 'MODULES_REGISTRY') and isinstance(mod.MODULES_REGISTRY, dict):
                supplier_modules.update(mod.MODULES_REGISTRY)
        except (ImportError, AttributeError):
            continue

    # 4️⃣ ✅ الخطوة الأهم: توليد روابط جاهزة داخل الموديولات بدلاً من مجرد Endpoints
    for key, module in supplier_modules.items():
        if 'links' in module and isinstance(module['links'], dict):
            final_links = {}
            for endpoint, title in module['links'].items():
                try:
                    if 'supplier_wallet' in endpoint:
                        # الحصول على wallet_id من المتغيرات المتاحة
                        wallet_id_val = get_current_wallet_identifier()
                        final_links[endpoint] = {'title': title, 'url': url_for(endpoint, wallet_id=wallet_id_val)}
                    else:
                        final_links[endpoint] = {'title': title, 'url': url_for(endpoint)}
                except BuildError:
                    # في حالة فشل بناء الرابط، نستخدم مسار احتياطي آمن
                    fallback_url = '/supplier/wallet/transactions' if 'supplier_wallet' in endpoint else '#'
                    final_links[endpoint] = {'title': title, 'url': fallback_url}
            module['links'] = final_links

    # 5️⃣ في حالة التعذر الكامل، يتم تقديم الموديول الحالي كقيمة احتياطية
    if not supplier_modules:
        wallet_id_val = get_current_wallet_identifier()
        supplier_modules['supplier_wallet'] = {
            'title': 'المحفظة الرقمية',
            'icon': 'fas fa-wallet',
            'links': {
                'supplier_wallet_bp.transactions': {'title': 'حركة المحفظة', 'url': url_for('supplier_wallet_bp.transactions', wallet_id=wallet_id_val)},
                'supplier_wallet_bp.process_withdraw': {'title': 'سحب الرصيد', 'url': url_for('supplier_wallet_bp.process_withdraw', wallet_id=wallet_id_val)}
            }
        }

    return supplier_modules


def get_current_wallet_identifier():
    """الحصول على المعرف الخاص بالمحفظة."""
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id
    if not supplier_id:
        return '1'
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


# --- مسارات إعادة التوجيه السريعة ---

@supplier_wallet_bp.route('/transactions', strict_slashes=False)
@login_required
def transactions_redirect():
    wallet_id = get_current_wallet_identifier()
    return redirect(url_for('supplier_wallet_bp.transactions', wallet_id=wallet_id))


@supplier_wallet_bp.route('/withdraw', strict_slashes=False)
@login_required
def withdraw_redirect():
    wallet_id = get_current_wallet_identifier()
    return redirect(url_for('supplier_wallet_bp.process_withdraw', wallet_id=wallet_id))


@supplier_wallet_bp.route('/', strict_slashes=False)
@supplier_wallet_bp.route('/dashboard', strict_slashes=False)
@login_required
def wallet_dashboard_redirect():
    wallet_id = get_current_wallet_identifier()
    return redirect(url_for('supplier_wallet_bp.transactions', wallet_id=wallet_id))


# --- مسارات اللوحة والصفحات المالية ---

@supplier_wallet_bp.route('/<string:wallet_id>/', strict_slashes=False)
@supplier_wallet_bp.route('/<string:wallet_id>/dashboard', strict_slashes=False)
@login_required
def wallet_dashboard(wallet_id):
    """إعادة توجيه تلقائية من مسار dashboard إلى سجل المعاملات."""
    return redirect(url_for('supplier_wallet_bp.transactions', wallet_id=wallet_id))


@supplier_wallet_bp.route('/<string:wallet_id>/transactions', strict_slashes=False)
@login_required
def transactions(wallet_id):
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id

    if not supplier_id:
        return safe_redirect_home()

    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if not wallet:
        try:
            wallet = WalletService.get_or_create_wallet(db.session, supplier_id, getattr(current_user, 'trade_name', 'متجر المورد'))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Transactions Wallet Error]: {str(e)}")
            traceback.print_exc()
            return safe_redirect_home()

    # ✅ جلب الحركات بالترتيب الزمني (من الأقدم للأحدث)
    transactions_list = WalletTransaction.query.filter_by(wallet_id=wallet.id).order_by(WalletTransaction.created_at.asc()).all()
    all_transactions = list(transactions_list)

    # ✅ إضافة الرصيد بعد كل حركة (balance_after) - حساب تراكمي للخلف
    running_balance = Decimal(str(wallet.balance))  # نبدأ من الرصيد الحالي
    for trx in reversed(all_transactions):
        trx.balance_after = running_balance
        if trx.transaction_type in ['credit', 'deposit']:
            running_balance = running_balance - Decimal(str(trx.amount))
        elif trx.transaction_type in ['debit', 'withdraw']:
            running_balance = running_balance + Decimal(str(trx.amount))

    # ✅ ترتيبهم من الأحدث للأقدم للعرض
    all_transactions.reverse()

    def get_sort_key(t):
        dt = getattr(t, 'created_at', None)
        return dt if dt is not None else datetime.min

    all_transactions.sort(key=get_sort_key, reverse=True)

    # ✅ جلب المورد
    supplier = Supplier.query.filter_by(id=supplier_id).first()

    # ✅ فلاتر البحث والفرز
    search_query = request.args.get('q', '').strip()
    trans_type = request.args.get('trans_type', '').strip()
    status = request.args.get('status', '').strip()

    # ✅ فلاتر تحديد الفترة
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            all_transactions = [t for t in all_transactions if t.created_at and t.created_at >= start_dt]
        except ValueError:
            pass

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            all_transactions = [t for t in all_transactions if t.created_at and t.created_at <= end_dt]
        except ValueError:
            pass

    if search_query:
        filtered_list = []
        for t in all_transactions:
            if isinstance(t, dict):
                v_num = str(t.get('voucher_number', '') or '')
                r_num = str(t.get('reference_number', '') or '')
            else:
                v_num = str(getattr(t, 'voucher_number', '') or '')
                r_num = str(getattr(t, 'reference_number', '') or '')
            if search_query.lower() in v_num.lower() or search_query.lower() in r_num.lower():
                filtered_list.append(t)
        all_transactions = filtered_list

    if trans_type:
        filtered_list = []
        for t in all_transactions:
            if isinstance(t, dict):
                t_type = t.get('transaction_type')
            else:
                t_type = getattr(t, 'transaction_type', None)
                if hasattr(t_type, 'value'):
                    t_type = t_type.value
            if str(t_type).lower() == trans_type.lower():
                filtered_list.append(t)
        all_transactions = filtered_list

    if status:
        filtered_list = []
        for t in all_transactions:
            if isinstance(t, dict):
                s_val = t.get('status')
            else:
                s_val = getattr(t, 'status', None)
                if hasattr(s_val, 'value'):
                    s_val = s_val.value
            if str(s_val).lower() == status.lower():
                filtered_list.append(t)
        all_transactions = filtered_list

    balance = get_wallet_balance(wallet)
    
    # ✅ استدعاء الدالة المحدثة التي تولد روابط جاهزة
    modules = get_sidebar_modules()

    return render_template(
        'supplier_wallet/wallet_transactions.html',
        wallet=wallet,
        balance=balance,
        transactions=all_transactions,
        supplier=supplier,
        supplier_modules=modules,
        modules_registry=modules,
        get_trx_type_attr=get_trx_type_attr,
        now=datetime.now()
    )


# =========================================================
# ✅ استيراد الملفات الفرعية (وضعها هنا بدون أي try/except فارغ)
# =========================================================
import apps.supplier_wallet.withdrawals_routes
import apps.supplier_wallet.receipt_routes
import apps.supplier_wallet.print_routes
