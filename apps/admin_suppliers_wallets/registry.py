MODULE_METADATA = {
    "module_id": "admin_suppliers_wallets",
    "name": "إدارة محافظ الموردين",
    "version": "2.4.0",
    "icon": "fas fa-wallet",
    "category": "Treasury & Settlements",
    "route_prefix": "/admin/suppliers-wallets",
    "permissions": [
        "view_suppliers_wallets",
        "freeze_supplier_wallet",
        "adjust_supplier_balance",
        "export_wallets_statement"
    ],
    "description": "إدارة أرصدة الموردين، حسابات الضمان (Escrow)، وعمليات السحب الفوري والتحقق البنكي عبر SAMA Sarie.",
    # إضافة روابط القائمة الجانبية هنا لكي يتمكن القالب الرئيسي من توليدها بشكل صحيح:
    "links": {
        "suppliers_wallets_controller.index": "قائمة المحافظ والأرصدة"
    }
}

def register_module(app):
    """تسجيل الموديول في تطبيق فلاسك المركزي"""
    from . import create_admin_suppliers_wallets_blueprint
    bp = create_admin_suppliers_wallets_blueprint()
    app.register_blueprint(bp, url_prefix=MODULE_METADATA["route_prefix"])
    print(f"✓ تم تسجيل موديول [{MODULE_METADATA['name']}] بنجاح في المنصة.")
