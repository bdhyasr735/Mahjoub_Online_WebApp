# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py

from flask import Blueprint

bp = Blueprint(
    'suppliers_auth_portal',
    __name__,
    template_folder='templates/suppliers_auth_portal',
    url_prefix='/suppliers'
)

from . import routes, seo_service

# ✅ تسجيل البلوبرنت الفرعي
bp.register_blueprint(routes.suppliers_auth_bp)

# ✅ إضافة دوال SEO
@bp.app_context_processor
def inject_seo():
    from .seo_service import get_seo_data, get_page_title, get_page_description
    return {
        'get_seo_data': get_seo_data,
        'get_page_title': get_page_title,
        'get_page_description': get_page_description
    }
