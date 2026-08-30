# apps/suppliers_auth_portal/registry.py

"""
ملف التسجيل لبوابة مصادقة الموردين
يستخدم لتسجيل البوابة وملحقاتها في التطبيق الرئيسي
"""

import logging
from apps.suppliers_auth_portal.routes import init_app

logger = logging.getLogger(__name__)

def register_suppliers_auth_portal(app):
    """تسجيل بوابة الموردين في تطبيق الفلاسك الرئيسي"""
    try:
        init_app(app)
        logger.info("✅ تم تسجيل بوابة مصادقة الموردين بنجاح عبر ملف التسجيل")
    except Exception as e:
        logger.error(f"❌ حدث خطأ أثناء تسجيل بوابة الموردين: {str(e)}")
        raise e
