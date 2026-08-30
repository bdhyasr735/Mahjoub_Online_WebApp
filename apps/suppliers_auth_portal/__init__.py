# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py

from flask import Blueprint

# ✅ إنشاء البلوبرنت الرئيسي للبوابة
bp = Blueprint(
    'suppliers_auth_portal',
    __name__,
    template_folder='templates/suppliers_auth_portal',
    url_prefix='/suppliers'
)

# ✅ استيراد ملف المسارات (auth_routes)
from . import auth_routes

# ✅ تسجيل البلوبرنت الفرعي (الذي يحتوي على جميع المسارات)
bp.register_blueprint(auth_routes.bp)

# ✅ إضافة دوال SEO إلى سياق القوالب (اختياري - للاستخدام مع base.html)
@bp.app_context_processor
def inject_seo():
    from .seo_service import get_seo_data, get_page_title, get_page_description
    return {
        'get_seo_data': get_seo_data,
        'get_page_title': get_page_title,
        'get_page_description': get_page_description
    }
