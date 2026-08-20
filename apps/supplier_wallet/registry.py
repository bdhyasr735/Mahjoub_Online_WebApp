# coding: utf-8
# 📂 apps/supplier_wallet/registry.py

import logging
from flask import url_for, Blueprint, has_app_context

supplier_wallet_bp = Blueprint(
    'supplier_wallet', 
    __name__,
    template_folder='templates',
    static_folder='static'
)

logger = logging.getLogger(__name__)

# المتغيرات الهيكلية التي يقرأها النظام
MODULE_NAME = "الإدارة المالية"
TITLE = "الإدارة المالية"
NAME = "supplier_wallet"
DISPLAY_NAME = "الإدارة المالية"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

LINKS = {
    "supplier_wallet.wallet_dashboard": "💳 كشف الحساب",
    "supplier_wallet.withdraw": "💸 طلب سحب"
}

def register_module(app):
    """تسجيل الموديول وتضمين القوائم في سياق القوالب"""
    try:
        if 'supplier_wallet' not in app.blueprints:
            try:
                # استيراد ملف المسارات لربط الدوال بـ supplier_wallet_bp
                from .routes import wallet_routes
            except ImportError:
                pass

            app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
            print("✅ [Registry Wallet]: تم تسجيل موديول الإدارة المالية بنجاح.")

        # ✅ حقن دمج القاموس بشكل صريح في supplier_modules
        @app.context_processor
        def inject_wallet_to_supplier_modules():
            wallet_module_data = {
                'title': TITLE,
                'icon': MODULE_ICON,
                'links': LINKS
            }
            
            # جلب القاموس الحالي إن وجد
            modules = getattr(app, 'supplier_modules', {})
            modules['supplier_wallet'] = wallet_module_data
            app.supplier_modules = modules

            return dict(
                supplier_modules=modules,
                SUPPLIER_WALLET_THEME_COLOR='#4A154B'
            )

    except Exception as e:
        print(f"❌ [Registry Wallet]: خطأ أثناء تسجيل supplier_wallet: {e}")
    return app

# باقي الدوال (get_module_stats, get_module_link, get_dashboard_card) تبقى كما هي...
