# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py

"""
بوابة المصادقة للموردين وموظفيهم
تسجيل وإدارة حسابات الموردين والموظفين
"""

import logging
from flask import Blueprint

logger = logging.getLogger(__name__)

# ============================================================
# تعريف الموديول
# ============================================================

MODULE_NAME = "بوابة الموردين"
MODULE_ICON = "fa-store"
SHOW_IN_SUPPLIER = False

NAV_ITEMS = [
    {'title': 'تسجيل الدخول', 'endpoint': 'suppliers_auth_bp.login_page', 'icon': 'fa-sign-in-alt'},
    {'title': 'اشتراك مورد جديد', 'endpoint': 'suppliers_auth_bp.register_page', 'icon': 'fa-user-plus'},
    {'title': 'استعادة كلمة المرور', 'endpoint': 'suppliers_auth_bp.forgot_password_page', 'icon': 'fa-key'},
]


# ============================================================
# دالة التهيئة
# ============================================================

def init_app(app):
    """تهيئة تطبيق Flask مع Blueprint المصادقة"""
    try:
        from .routes import suppliers_auth_bp
        app.register_blueprint(suppliers_auth_bp)
        logger.info("✅ تم تهيئة بوابة مصادقة الموردين بنجاح")
        return True
    except Exception as e:
        logger.error(f"❌ فشل تهيئة بوابة مصادقة الموردين: {e}")
        return False


# ============================================================
# دالة تسجيل الموديول
# ============================================================

def register_module(app):
    """تسجيل الموديول في التطبيق (للتسجيل الديناميكي)"""
    try:
        from .routes import suppliers_auth_bp
        app.register_blueprint(suppliers_auth_bp)
        logger.info("✅ [بوابة الموردين]: تم تسجيل بوابة الموردين بنجاح.")
        return True
    except Exception as e:
        logger.error(f"❌ [خطأ بوابة الموردين]: فشل تسجيل بوابة الموردين: {e}")
        return False


# ============================================================
# تصدير Blueprint للاستخدام المباشر
# ============================================================

# محاولة استيراد الـ Blueprint من routes
try:
    from .routes import suppliers_auth_bp
except ImportError:
    # إذا فشل الاستيراد، إنشاء Blueprint جديد
    suppliers_auth_bp = Blueprint(
        'suppliers_auth_bp',
        __name__,
        template_folder='templates/suppliers_auth_portal',
        static_folder='static/suppliers_auth_portal',
        url_prefix='/supplier'
    )
    logger.warning("⚠️ [بوابة الموردين]: تم إنشاء Blueprint جديد (لم يتم استيراده من routes)")


# ============================================================
# نقطة الدخول للتشغيل المستقل
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🔐 Suppliers Auth Portal - Module")
    print("=" * 60)
    print(f"📌 Module Name: {MODULE_NAME}")
    print(f"📌 Blueprint: suppliers_auth_bp")
    print(f"📌 URL Prefix: /supplier")
    print("=" * 60)
    print("✅ Module loaded successfully")
