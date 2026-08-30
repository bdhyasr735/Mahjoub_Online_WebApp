bp = Blueprint(
    'suppliers_auth_portal',  # ✅ هذا هو اسم البلوبرنت الرئيسي
    __name__,
    template_folder='templates/suppliers_auth_portal',
    url_prefix='/suppliers'
)

from . import routes
bp.register_blueprint(routes.suppliers_auth_bp)  # ✅ هذا هو الـ Blueprint الفرعي
