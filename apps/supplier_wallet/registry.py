# coding: utf-8
# 📂 apps/supplier_wallet/registry.py

import logging
from flask import url_for, session, current_app
from flask_login import current_user

logger = logging.getLogger(__name__)

MODULE_NAME = "المحفظة الرقمية"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# ✅ التعديل الجوهري هنا:
# استخدام أسماء الدوال (endpoints) الحقيقية الموجودة في routes.py
LINKS = {
    "supplier_wallet_bp.transactions": "حركة المحفظة",
    "supplier_wallet_bp.withdraw": "سحب الرصيد"
}


def register_module(app):
    """تسجيل موديول المحفظة الرقمية في التطبيق."""
    try:
        from apps.supplier_wallet.routes import supplier_wallet_bp
        
        if 'supplier_wallet_bp' not in app.blueprints:
            app.register_blueprint(supplier_wallet_bp)
            print("✅ [Registry Supplier Wallet]: تم تسجيل موديول المحفظة الرقمية.")
        else:
            print("ℹ️ [Registry Supplier Wallet]: موديول المحفظة الرقمية مسجل مسبقاً.")
            
        # ✅ محاولة استيراد الموديولات الفرعية
        try:
            import apps.supplier_wallet.receipt_routes
            import apps.supplier_wallet.print_routes
            import apps.supplier_wallet.withdrawals_routes
        except ImportError as e:
            print(f"ℹ️ [Registry Supplier Wallet]: تم تحميل الموديولات الفرعية (بعضها قد لا يكون موجوداً): {e}")
            
    except ImportError as e:
        print(f"❌ [Registry Supplier Wallet]: خطأ في استيراد routes: {e}")
    except Exception as e:
        print(f"❌ [Registry Supplier Wallet]: خطأ في تسجيل supplier_wallet: {e}")
    return app


def get_supplier_id():
    """الحصول على معرف المورد من مصادر متعددة."""
    supplier_id = session.get('user_id') or session.get('supplier_id')
    
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id
        
    if not supplier_id and hasattr(current_app, 'config'):
        supplier_id = current_app.config.get('TEST_SUPPLIER_ID')
        
    return supplier_id


def get_module_stats():
    """جلب إحصائيات المحفظة."""
    try:
        from apps.models.wallet_db import SupplierWallet, WalletTransaction, WithdrawalRequest
        from sqlalchemy import func

        supplier_id = get_supplier_id()
        
        if not supplier_id:
            return {
                'balance': 0.0,
                'pending_withdrawals': 0,
                'total_transactions': 0,
                'has_wallet': False,
                'wallet_code': None
            }

        wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        
        if not wallet:
            return {
                'balance': 0.0,
                'pending_withdrawals': 0,
                'total_transactions': 0,
                'has_wallet': False,
                'wallet_code': None
            }

        balance = float(getattr(wallet, 'balance', 0) or getattr(wallet, 'balance_sar', 0) or 0)
        
        pending_withdrawals = WithdrawalRequest.query.filter_by(
            wallet_id=wallet.id, 
            status='pending'
        ).count()
        
        total_transactions = WalletTransaction.query.filter_by(
            wallet_id=wallet.id
        ).count()

        return {
            'balance': balance,
            'pending_withdrawals': pending_withdrawals,
            'total_transactions': total_transactions,
            'has_wallet': True,
            'wallet_code': getattr(wallet, 'wallet_code', None) or str(wallet.id)
        }
        
    except Exception as e:
        logger.error(f"❌ [Registry Supplier Wallet Stats Error]: {e}")
        import traceback
        traceback.print_exc()
        return {
            'balance': 0.0,
            'pending_withdrawals': 0,
            'total_transactions': 0,
            'has_wallet': False,
            'wallet_code': None,
            'error': str(e)
        }


def get_module_link():
    """الحصول على رابط الموديول."""
    try:
        # ✅ الآن يشير للصفحة الحقيقية (وليس الـ redirect)
        return url_for('supplier_wallet_bp.transactions', wallet_id=get_current_wallet_identifier())
    except Exception as e:
        logger.warning(f"⚠️ [Registry Supplier Wallet Link Error]: {e}")
        # ✅ حل آمن: استخدام المسار المباشر
        return '/supplier/wallet/transactions'


def get_dashboard_card():
    """الحصول على بطاقة لوحة التحكم للموديول."""
    stats = get_module_stats()
    
    balance_str = f"{stats.get('balance', 0.0):,.2f} ر.س"
    
    if stats.get('balance', 0) > 100000:
        color = 'gold'
    elif stats.get('balance', 0) > 10000:
        color = 'purple'
    elif stats.get('balance', 0) > 1000:
        color = 'blue'
    else:
        color = 'gray'
    
    return {
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'link': get_module_link(),
        'stats': stats,
        'color': color,
        'badge': balance_str,
        'subtitle': f"{stats.get('pending_withdrawals', 0)} طلبات سحب معلقة",
        'wallet_code': stats.get('wallet_code', '---')
    }


def get_nav_metadata():
    """الحصول على بيانات القائمة الجانبية للموديول."""
    return {
        'key': 'supplier_wallet',
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'show_in_supplier': SHOW_IN_SUPPLIER,
        'links': LINKS,
        'priority': 10,
        'badge': lambda: f"{get_module_stats().get('pending_withdrawals', 0)}"
    }


# ✅ تصدير الكل
__all__ = [
    'MODULE_NAME', 
    'MODULE_ICON', 
    'SHOW_IN_SUPPLIER', 
    'LINKS', 
    'register_module', 
    'get_module_stats', 
    'get_module_link', 
    'get_dashboard_card',
    'get_nav_metadata'
]
