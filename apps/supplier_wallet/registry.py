# coding: utf-8
# 📂 apps/supplier_wallet/registry.py

from apps.supplier_wallet.routes import supplier_wallet_bp

# يجب تغيير الاسم هنا إلى 'register_module' ليتعرف عليها المصنع تلقائياً
def register_module(app):
    """
    دالة موحدة لتسجيل الموديول، يتوقع المصنع هذا الاسم.
    """
    app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
    print("✅ [Registry] تم تسجيل موديول 'محفظة المورد' بنجاح.")
