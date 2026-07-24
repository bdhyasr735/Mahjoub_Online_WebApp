# 📂 apps/suppliers_product/registry.py

from apps.suppliers_product.routes import suppliers_product_bp, add_product_bp, edit_product_bp

MODULE_NAME = "منتجاتي"
MODULE_ICON = "fas fa-boxes"
SHOW_IN_SUPPLIER = True

LINKS = {
    "suppliers_product_bp.products": "📦 منتجاتي",
    "add_product_bp.add_product_page": "➕ إضافة منتج"
}


def register_module(app):
    app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')
    app.register_blueprint(add_product_bp, url_prefix='/supplier')
    app.register_blueprint(edit_product_bp, url_prefix='/supplier')
    print("✅ [Registry]: تم تسجيل موديول 'منتجاتي'")
