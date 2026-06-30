from apps.admin_platform_treasury.routes import treasury_bp

def register_module(app):
    app.register_blueprint(treasury_bp, url_prefix='/admin/treasury')
