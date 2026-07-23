# coding: utf-8
# 📂 apps/supplier_wallet/registry.py

"""
تسجيل تطبيق محفظة المورد في المنصة
"""

MODULE_NAME = "محفظة المورد"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# ✅ الروابط الصحيحة - استخدم المسار الصحيح
LINKS = {
    'supplier_wallet.view_my_wallet': '💰 محفظتي'
}


def register_module(app):
    """تسجيل تطبيق محفظة المورد"""
    try:
        from apps.supplier_wallet.routes import supplier_wallet_bp
        
        if 'supplier_wallet' not in app.blueprints:
            app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier')
            print("✅ [Registry]: تم تسجيل 'supplier_wallet'")
        else:
            print("ℹ️ [Registry]: 'supplier_wallet' مسجل مسبقاً")
            
    except ImportError as e:
        print(f"❌ [Registry]: خطأ في استيراد supplier_wallet: {e}")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل supplier_wallet: {e}")
    
    return app
