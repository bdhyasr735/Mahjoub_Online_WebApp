# 📂 apps/admin_financial_control/registry.py

MODULE_NAME = "الرقابة المالية"
MODULE_ICON = "fas fa-shield-alt"

# تأكد أن النظام يقرأ الروابط بهذا الشكل
LINKS = {
    "الخزينة المركزية": "treasury_bp.dashboard",
    "محفظة الموردين": "wallet_app.dashboard",
    "أسعار الصرف": "admin_exchange.manage_rates" 
}

def register_module(app):
    print("✅ [Registry]: تم تسجيل موديول 'الرقابة المالية' بنجاح.")
