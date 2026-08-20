# coding: utf-8
# 📂 apps/supplier_wallet/registry.py

import logging
from flask import has_app_context, url_for

logger = logging.getLogger(__name__)

MODULE_NAME = "الإدارة المالية"
TITLE = "الإدارة المالية"
NAME = "supplier_wallet"
DISPLAY_NAME = "الإدارة المالية"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

NAV_ITEMS = [
    {"endpoint": "supplier_wallet.wallet_dashboard", "title": "💳 كشف الحساب"},
    {"endpoint": "supplier_wallet.withdraw", "title": "💸 طلب سحب"}
]

LINKS = {
    "supplier_wallet.wallet_dashboard": "💳 كشف الحساب",
    "supplier_wallet.withdraw": "💸 طلب سحب"
}

def register_module(app):
    """تسجيل الموديول والـ Blueprints وتغذية القوائم"""
    # 1. تسجيل الـ Blueprint
    try:
        from apps.supplier_wallet import supplier_wallet_bp
        if 'supplier_wallet' not in app.blueprints:
            app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
    except Exception as e:
        logger.error(f"❌ [Registry Wallet Error]: فشل تسجيل الـ Blueprint: {e}")

    # 2. حقن الموديول في سياق القوالب (التوافق الكامل)
    @app.context_processor
    def inject_supplier_wallet_meta():
        # التأكد من تهيئة القاموس في التطبيق إذا لم يكن موجوداً
        if not hasattr(app, 'supplier_modules'):
            app.supplier_modules = {}

        # إضافة الموديول للقاموس المشترك
        app.supplier_modules['supplier_wallet'] = {
            'title': TITLE,
            'icon': MODULE_ICON,
            'links': LINKS,
            'nav_items': NAV_ITEMS,
            'show_in_supplier': SHOW_IN_SUPPLIER
        }

        return dict(
            supplier_modules=app.supplier_modules,
            SUPPLIER_WALLET_THEME_COLOR='#4A154B',
            DEFAULT_PER_PAGE=10
        )

    return app

def get_module_stats():
    """جلب إحصائيات المحفظة"""
    if not has_app_context():
        return {'total_balance': '0.00', 'available_balance': '0.00', 'pending_balance': '0.00', 'has_wallet': False, 'currency': 'ر.س'}
    
    try:
        from apps.extensions import db
        from apps.models.wallet_db import SupplierWallet, WalletTransaction
        from apps.supplier_wallet.utils import get_current_supplier_id, get_trx_type_attr

        supplier_id = get_current_supplier_id()
        if not supplier_id: return {'total_balance': '0.00', 'available_balance': '0.00', 'pending_balance': '0.00', 'has_wallet': False, 'currency': 'ر.س'}

        wallet_obj = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        if not wallet_obj: return {'total_balance': '0.00', 'available_balance': '0.00', 'pending_balance': '0.00', 'has_wallet': False, 'currency': 'ر.س'}

        trx_type_col = get_trx_type_attr()

        # حساب الرصيد المعلق
        q_pending = db.session.query(db.func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.wallet_id == wallet_obj.id, WalletTransaction.status == 'pending'
        )
        if trx_type_col is not None: q_pending = q_pending.filter(trx_type_col == 'credit')
        pending_credits = float(q_pending.scalar() or 0.00)

        # حساب المسحوبات
        q_withdrawn = db.session.query(db.func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.wallet_id == wallet_obj.id, WalletTransaction.status.in_(['completed', 'pending'])
        )
        if trx_type_col is not None: q_withdrawn = q_withdrawn.filter(trx_type_col.in_(['withdrawal', 'debit']))
        total_withdrawn = float(q_withdrawn.scalar() or 0.00)

        raw_bal = float(getattr(wallet_obj, 'balance_sar', 0.00))
        avail_bal = max(0.00, raw_bal - total_withdrawn)
        tot_bal = avail_bal + pending_credits

        return {
            'total_balance': f"{tot_bal:,.2f}",
            'available_balance': f"{avail_bal:,.2f}",
            'pending_balance': f"{pending_credits:,.2f}",
            'has_wallet': True,
            'currency': getattr(wallet_obj, 'currency', 'ر.س')
        }
    except Exception as e:
        logger.error(f"❌ [Registry Wallet Stats Error]: {e}")
        return {'total_balance': '0.00', 'available_balance': '0.00', 'pending_balance': '0.00', 'has_wallet': False, 'currency': 'ر.س'}

def get_module_link():
    try: return url_for('supplier_wallet.wallet_dashboard')
    except Exception: return '/supplier/wallet/dashboard'

def get_dashboard_card():
    stats = get_module_stats()
    return {
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'link': get_module_link(),
        'stats': stats,
        'color': 'purple',
        'badge': stats.get('available_balance', '0.00'),
        'subtitle': f"المتاح: {stats.get('available_balance', '0.00')} {stats.get('currency', 'ر.س')}"
    }
