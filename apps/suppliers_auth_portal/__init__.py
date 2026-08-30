from flask import Blueprint

bp = Blueprint(
    'suppliers_auth_portal',
    __name__,
    template_folder='templates/suppliers_auth_portal',
    url_prefix='/supplier'          # ✅ البادئة هنا
)

from . import auth_login, auth_register, auth_recovery

bp.register_blueprint(auth_login.bp)
bp.register_blueprint(auth_register.bp)
bp.register_blueprint(auth_recovery.bp)
