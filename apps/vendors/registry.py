# coding: utf-8
# 📂 apps/vendors/registry.py - التسجيل التلقائي لنظام الموردين

from apps.vendors.routes import vendors_bp

def register_app(app):
    """
    دالة التسجيل التلقائي التي يستدعيها المصنع الرئيسي (apps/__init__.py)
    لربط مسارات الموردين بالتطبيق دون تعديل الملف الرئيسي.
    """
    app.register_blueprint(vendors_bp)
    print("✅ [System] تم تسجيل Blueprint الموردين بنجاح عبر النظام التلقائي.")
