"""
apps/admin_treasury/registry.py
تسجيل موديول الخزينة المركزية في لوحة الإدارة الرئيسية
مشروع Mahjoub Online WebApp
"""

class AdminTreasuryModuleRegistry:
    """
    سجل معلومات وصلاحيات موديول الخزينة المركزية
    """
    MODULE_KEY = "admin_treasury"
    DISPLAY_NAME = "الخزينة المركزية وحسابات الضمان"
    ICON = "landmark"
    VERSION = "2.4.0"
    URL_PREFIX = "/admin/treasury"
    REQUIRED_PERMISSION = "manage_platform_treasury"

    NAV_ITEMS = [
        {
            "id": "treasury_overview",
            "title": "نظرة عامة والسيولة",
            "endpoint": "admin_treasury.treasury_index",
            "icon": "wallet",
            "permission": "view_treasury"
        },
        {
            "id": "treasury_ledger",
            "title": "دفتر الأستاذ والقيود",
            "endpoint": "admin_treasury.treasury_ledger",
            "icon": "book-open",
            "permission": "view_treasury_ledger"
        },
        {
            "id": "escrow_reserve",
            "title": "حسابات الضمان (Escrow)",
            "endpoint": "admin_treasury.escrow_management",
            "icon": "shield-check",
            "permission": "manage_escrow"
        },
        {
            "id": "bank_reconciliation",
            "title": "التسويات البنكية",
            "endpoint": "admin_treasury.bank_accounts",
            "icon": "building-2",
            "permission": "manage_bank_accounts"
        }
    ]

    @classmethod
    def get_nav_metadata(cls):
        return {
            "key": cls.MODULE_KEY,
            "name": cls.DISPLAY_NAME,
            "icon": cls.ICON,
            "url": cls.URL_PREFIX,
            "items": cls.NAV_ITEMS
        }
