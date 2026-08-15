from flask import Blueprint

def create_admin_suppliers_wallets_blueprint():
    bp = Blueprint(
        'admin_suppliers_wallets',
        __name__,
        template_folder='templates',
        static_folder='static',
        url_prefix='/admin/suppliers-wallets'
    )
    
    from .routes import suppliers_wallets_controller
    bp.register_blueprint(suppliers_wallets_controller.bp)
    
    return bp
