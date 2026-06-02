from apps.add_supplier.routes import add_supplier as add_supplier_bp
safe_register(add_supplier_bp, url_prefix='/suppliers')
