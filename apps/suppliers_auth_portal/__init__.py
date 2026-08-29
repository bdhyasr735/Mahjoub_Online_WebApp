from flask import Blueprint

suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',  # ← هذا الاسم اللي نستخدمه في url_for
    __name__,
    template_folder='templates',
    url_prefix='/suppliers'
)
