# coding: utf-8
from .routes import suppliers_bp

# 1. إعدادات الموديول (مطابقة للنظام الجديد)
MODULE_NAME = "بوابة الموردين"
MODULE_ICON = "fas fa-lock"
SHOW_IN_SUPPLIER = False # لن يظهر في القائمة الجانبية

LINKS = {
    "تسجيل الدخول": "suppliers_auth.login"
}

def register_module(app):
    """
    تسجيل موديول Auth الموحد
    """
    try:
        # توحيد المسار ليطابق ما يوجد في __init__.py
        app.register_blueprint(suppliers_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل بوابة المورد بنجاح على المسار /supplier")
    except Exception as e:
        print(f"🚨 [Registry Error]: {e}")
