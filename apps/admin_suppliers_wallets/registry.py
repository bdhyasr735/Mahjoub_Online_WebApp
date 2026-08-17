"""
سجل موديول محافظ الموردين وإعدادات الصلاحيات والـ Menu Registration
"""

MODULE_METADATA = {
    "module_id": "admin_suppliers_wallets",
    "name": "إدارة محافظ الموردين",
    "version": "2.4.0",
    "icon": "wallet",
    # ✅ تم تغيير التصنيف ليتناسب مع قسم "إدارة المحافظ/الموردين"
    "category": "Supplier Management",
    "route_prefix": "/admin/suppliers-wallets",
    "permissions": [
        "view_suppliers_wallets",
        "freeze_supplier_wallet",
        "adjust_supplier_balance",
        "export_wallets_statement",
        "manage_withdraw_requests"
    ],
    "description": "إدارة أرصدة الموردين، حسابات الضمان (Escrow)، وعمليات السحب الفوري والتحقق البنكي عبر SAMA Sarie.",
    # ✅ تم تغيير العنوان إلى "طلبات السحب" ليتطابق مع طلبك
    "menu_items": [
        {
            "title": "طلبات السحب",
            "icon": "money-bill-transfer",
            "route": "/admin/suppliers-wallets/withdraw-requests",
            "permission": "manage_withdraw_requests"
        }
    ]
}

def register_module(app):
    """تسجيل الموديول في تطبيق فلاسك المركزي"""
    from . import create_admin_suppliers_wallets_blueprint
    bp = create_admin_suppliers_wallets_blueprint()
    app.register_blueprint(bp)
    print(f"✓ تم تسجيل موديول [{MODULE_METADATA['name']}] بنجاح في المنصة.")
