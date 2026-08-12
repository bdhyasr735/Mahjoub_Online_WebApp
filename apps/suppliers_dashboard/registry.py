# coding: utf-8
# 📂 apps/suppliers_dashboard/registry.py

MODULE_NAME = "لوحة التحكم"
MODULE_ICON = "fas fa-home"
SHOW_IN_SUPPLIER = True

LINKS = {
    'suppliers_dashboard.dashboard': '📊 لوحة التحكم',
    'suppliers_wallet.wallet': '💰 المحفظة',
    'suppliers_wallet.withdraw': '💳 سحب الرصيد',
}


def register_module(app):
    """تسجيل جميع Blueprints الخاصة بلوحة تحكم الموردين"""
    try:
        # ✅ استيراد الـ Blueprints المتاحة فقط
        from apps.suppliers_dashboard.dashboard_routes import suppliers_dashboard_bp
        
        # ⚠️ استيراد اختياري للمحفظة إذا كانت موجودة في نفس الموديول
        try:
            from apps.suppliers_dashboard.wallet_routes import wallet_bp
        except ImportError:
            wallet_bp = None

        # ✅ تسجيل Blueprint لوحة التحكم الرئيسية
        if 'suppliers_dashboard' not in app.blueprints:
            app.register_blueprint(suppliers_dashboard_bp, url_prefix='/supplier')
            print("✅ [Registry]: تم تسجيل 'suppliers_dashboard'")
        else:
            print("ℹ️ [Registry]: 'suppliers_dashboard' مسجل مسبقاً")

        # ✅ تسجيل Blueprint المحفظة (إن وجد)
        if wallet_bp and 'suppliers_wallet' not in app.blueprints:
            app.register_blueprint(wallet_bp, url_prefix='/supplier')
            print("✅ [Registry]: تم تسجيل 'suppliers_wallet'")

    except ImportError as e:
        print(f"❌ [Registry]: خطأ في استيراد Blueprint: {e}")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل suppliers_dashboard: {e}")

    return app
