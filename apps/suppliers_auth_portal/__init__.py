# apps/suppliers_auth_portal/__init__.py

bp = Blueprint(
    'suppliers_auth_portal',
    __name__,
    template_folder='templates/suppliers_auth_portal',  # ✅ المسار الصحيح
    url_prefix='/supplier'
)
