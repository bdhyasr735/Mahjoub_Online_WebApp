# 📂 apps/admin_financial_control/registry.py

MODULE_NAME = "الرقابة المالية"
MODULE_ICON = "fas fa-shield-alt"

# هنا نضع الروابط التي تريدها تحت هذا الموديول
LINKS = {
    "الخزينة المركزية": "treasury_bp.dashboard",
    "محفظة الموردين": "wallet_app.dashboard"
}

def register_module(app):
    # لا نحتاج تسجيل Blueprint هنا، فقط نستخدم هذا الموديول لتجميع الروابط
    pass
