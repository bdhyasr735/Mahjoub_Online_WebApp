# -*- coding: utf-8 -*-
"""
ملف التسجيل لبوابة مصادقة الموردين
يستخدم لتسجيل البوابة وملحقاتها في التطبيق الرئيسي
"""

import logging
from apps.suppliers_auth_portal.routes import suppliers_auth_bp

logger = logging.getLogger(__name__)

def register_module(app):
    """تسجيل بوابة الموردين في تطبيق الفلاسك الرئيسي"""
    try:
        if suppliers_auth_bp.name not in app.blueprints:
            app.register_blueprint(suppliers_auth_bp, url_prefix='/supplier')
            from apps.extensions import csrf
            csrf.exempt(suppliers_auth_bp)
            logger.info("✅ تم تسجيل بوابة مصادقة الموردين بنجاح عبر ملف التسجيل")
        else:
            logger.info("✅ بوابة مصادقة الموردين مسجلة بالفعل")
    except Exception as e:
        logger.error(f"❌ حدث خطأ أثناء تسجيل بوابة الموردين: {str(e)}")
        raise e
