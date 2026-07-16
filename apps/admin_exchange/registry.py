# coding: utf-8
# 📂 apps/admin_exchange/registry.py

from apps.admin_exchange.routes import admin_exchange_bp

MODULE_NAME = "العملات والصرف"
MODULE_ICON = "fas fa-exchange-alt"

# تم تصحيح اسم المسار هنا ليتطابق مع الدالة 'manage_rates' في ملف routes.py
LINKS = {
    "admin_exchange_bp.manage_rates": "إدارة أسعار الصرف"
}

def register_module(app):
    try:
        app.register_blueprint(admin_exchange_bp, url_prefix='/admin/exchange')
        print("✅ [Registry]: تم تسجيل موديول 'admin_exchange' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول الصرف: {e}")
