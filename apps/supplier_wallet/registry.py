# coding: utf-8
# 📂 apps/supplier_wallet/registry.py

import logging
from flask import url_for, Blueprint, has_app_context

# تعريف الـ Blueprint هنا لضمان وجوده في الموديول
supplier_wallet_bp = Blueprint(
    'supplier_wallet', 
    __name__,
    template_folder='templates',
    static_folder='static'
)

logger = logging.getLogger(__name__)

# المسميات العربية للسلايدر
MODULE_NAME = "الرقابة المالية"
TITLE = "الرقابة المالية"
NAME = "الرقابة المالية"
DISPLAY_NAME = "الرقابة المالية"

MODULE_ICON = "fa-wallet"
SHOW_IN_SUPPLIER = True

LINKS = {
    "supplier_wallet.wallet": "💳 كشف الحساب",
    "supplier_wallet.withdraw": "💸 طلب سحب"
}

def register_module(app):
    """تسجيل الموديول وسياق القوالب"""
    try:
        if 'supplier_wallet' not in app.blueprints:
            app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
            print("✅ [Registry Wallet]: تم تسجيل موديول الرقابة المالية بنجاح.")
        else:
            print("ℹ️ [Registry Wallet]: موديول الرقابة المالية مسجل مسبقاً.")

        @app.context_processor
        def inject_supplier_wallet_meta():
            return dict(
                SUPPLIER_WALLET_THEME_COLOR='#4A154B',
                DEFAULT_PER_PAGE=10
            )

    except Exception as e:
        print(f"❌ [Registry Wallet]: خطأ أثناء تسجيل supplier_wallet: {e}")
    return app


def get_module_stats():
    """جلب إحصائيات المحفظة الحقيقية المباشرة من قاعدة البيانات للمورد الحالي"""
    if not has_app_context():
        return {'total_balance': '0.00', 'available_balance': '0.00', 'pending_balance': '0.00', 'has_wallet': False, 'currency': 'ر.س'}

    try:
        from apps.extensions import db
        from apps.models.wallet_db import SupplierWallet, WalletTransaction
        # استيراد الدوال المساعدة من الملف المخصص لها
        from apps.supplier_wallet.utils import get_current_supplier_id, get_trx_type_attr

        supplier_id = get_current_supplier_id()
        if not supplier_id:
            return {'total_balance': '0.00', 'available_balance': '0.00', 'pending_balance': '0.00', 'has_wallet': False, 'currency': 'ر.س'}

        wallet_obj = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        if not wallet_obj:
            return {'total_balance': '0.00', 'available_balance': '0.00', 'pending_balance': '0.00', 'has_wallet': False, 'currency': 'ر.س'}

        trx_type_col = get_trx_type_attr()

        # حساب الرصيد المعلق
        q_pending = db.session.query(db.func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.wallet_id == wallet_obj.id,
            WalletTransaction.status == 'pending'
        )
        if trx_type_col is not None:
            q_pending = q_pending.filter(trx_type_col == 'credit')
        pending_credits = float(q_pending.scalar() or 0.00)

        # حساب المسحوبات المكتملة أو قيد المعالجة
        q_withdrawn = db.session.query(db.func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.wallet_id == wallet_obj.id,
            WalletTransaction.status.in_(['completed', 'pending'])
        )
        if trx_type_col is not None:
            q_withdrawn = q_withdrawn.filter(trx_type_col.in_(['withdrawal', 'debit']))
        total_withdrawn = float(q_withdrawn.scalar() or 0.00)

        # الرصيد المتاح والإجمالي
        raw_bal = float(getattr(wallet_obj, 'balance_sar', 0.00))
        avail_bal = max(0.00, raw_bal - total_withdrawn)
        tot_bal = avail_bal + pending_credits
        currency = getattr(wallet_obj, 'currency', 'ر.س')

        return {
            'total_balance': f"{tot_bal:,.2f}",
            'available_balance': f"{avail_bal:,.2f}",
            'pending_balance': f"{pending_credits:,.2f}",
            'has_wallet': True,
            'currency': currency
        }
    except Exception as e:
        logger.error(f"❌ [Registry Wallet Stats Error]: {e}")
        return {'total_balance': '0.00', 'available_balance': '0.00', 'pending_balance': '0.00', 'has_wallet': False, 'currency': 'ر.س'}


def get_module_link():
    """الحصول على رابط المحفظة الرئيسي"""
    try:
        return url_for('supplier_wallet.wallet')
    except:
        return '/supplier/wallet/'


def get_dashboard_card():
    """توليد كارت لوحة التحكم"""
    stats = get_module_stats()
    curr = stats.get('currency', 'ر.س')
    avail = stats.get('available_balance', '0.00')

    return {
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'link': get_module_link(),
        'stats': stats,
        'color': 'purple',
        'badge': avail,
        'subtitle': f"المتاح: {avail} {curr}"
    }
