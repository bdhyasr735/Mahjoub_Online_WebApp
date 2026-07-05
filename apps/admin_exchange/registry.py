# 📂 apps/admin_exchange/registry.py

from apps.exchange.exchange_routes import admin_exchange_bp

# تعريف بيانات الموديول ليتم التعرف عليه في لوحة التحكم المركزية
MODULE_NAME = "أسعار الصرف"
MODULE_ICON = "fas fa-exchange-alt"

def register_module(app):
    """
    تسجيل موديول إدارة أسعار الصرف في التطبيق
    """
    app.register_blueprint(admin_exchange_bp, url_prefix='/admin/exchange')
    
    print("✅ [Registry]: تم تسجيل موديول 'Exchange' بنجاح.")

# إضافة إعدادات الروابط لتظهر في القائمة الجانبية (Sidebar) في لوحة الإدارة
LINKS = {
    "إدارة أسعار الصرف": "admin_exchange.manage_rates"
}
