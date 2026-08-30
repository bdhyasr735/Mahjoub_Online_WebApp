# apps/suppliers_auth_portal/registry.py

"""
سجل المصادقة - بوابة الموردين وموظفيهم
نسخة بسيطة وخفيفة تعتمد على النماذج الموجودة
"""

import logging
from flask import Blueprint

logger = logging.getLogger(__name__)

# ============================================================
# إنشاء Blueprint
# ============================================================

suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    template_folder='templates/suppliers_auth_portal',
    static_folder='static/suppliers_auth_portal',
    url_prefix='/suppliers'
)


# ============================================================
# استيراد المسارات (Routes)
# ============================================================

# يتم استيراد المسارات من ملف منفصل لتجنب التكرار
from . import routes


# ============================================================
# دالة التهيئة
# ============================================================

def init_app(app):
    """تهيئة التطبيق مع Blueprint المصادقة"""
    app.register_blueprint(suppliers_auth_bp)
    logger.info("✅ تم تهيئة بوابة مصادقة الموردين")
    return app


# ============================================================
# نقطة الدخول للتشغيل المستقل
# ============================================================

if __name__ == '__main__':
    print("=" * 50)
    print("🔐 Suppliers Auth Portal")
    print("=" * 50)
    print(f"📌 Blueprint: {suppliers_auth_bp.name}")
    print(f"📌 URL Prefix: {suppliers_auth_bp.url_prefix}")
    print("=" * 50)
    print("✅ Registry loaded successfully")
