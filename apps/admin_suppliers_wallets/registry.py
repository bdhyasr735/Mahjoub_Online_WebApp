# coding: utf-8
"""
سجل موديول محافظ الموردين وطلبات السحب (Metadata & Permissions)
مشروع Mahjoub Online WebApp
"""

MODULE_KEY = "admin_suppliers_wallets"
MODULE_NAME = "إدارة محافظ الموردين"
DISPLAY_NAME = "محافظ الموردين"
MODULE_ICON = "fas fa-wallet"
ICON = "wallet"
VERSION = "2.4.0"
URL_PREFIX = "/admin/suppliers-wallets"
REQUIRED_PERMISSION = "view_suppliers_wallets"
SHOW_IN_ADMIN = False  # تم إخفاؤه هنا لأنه مُدرج وينتظم تحت قائمة "الرقابة المالية"

MODULE_METADATA = {
    "module_id": MODULE_KEY,
    "name": MODULE_NAME,
    "version": VERSION,
    "icon": ICON,
    "category": "Treasury & Settlements",
    "route_prefix": URL_PREFIX,
    "permissions": [
        "view_suppliers_wallets",
        "freeze_supplier_wallet",
        "adjust_supplier_balance",
        "export_wallets_statement",
        "manage_withdraw_requests"
    ],
    "description": "إدارة أرصدة الموردين، حسابات الضمان، وعمليات السحب تحت الرقابة المالية."
}

def get_nav_metadata():
    return {
        "key": MODULE_KEY,
        "name": DISPLAY_NAME,
        "icon": ICON,
        "url": URL_PREFIX,
        "items": [],
        "show_in_admin": SHOW_IN_ADMIN
    }

def register_module(app):
    """
    تمت عملية التسجيل والربط الفعلي للـ Blueprint والمسارات 
    مباشرة عبر موديول الرقابة المالية (الخزينة) لضمان عمل الروابط بكفاءة.
    """
    pass
