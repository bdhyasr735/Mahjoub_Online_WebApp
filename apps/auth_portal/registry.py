# -*- coding: utf-8 -*-
# 📂 apps/auth_portal/registry.py

from flask import Blueprint

# اسم الموديول وعرضه في لوحة التحكم الإدارية
MODULE_NAME = "إدارة المصادقة والصلاحيات"
MODULE_ICON = "fa-shield-alt"

# تحديد ما إذا كان يظهر في لوحة الموردين أم الإدارة
SHOW_IN_SUPPLIER = False

# الروابط التي ستظهر في القائمة الجانبية للإدارة
NAV_ITEMS = [
    {
        'endpoint': 'auth.admin_login',
        'title': 'تسجيل دخول الإدارة'
    },
    {
        'endpoint': 'auth.admin_logout',
        'title': 'تسجيل الخروج'
    }
]

def register_module(app):
    """دالة التسجيل الديناميكي المطلوبة في هيكلية محجوب أونلاين"""
    try:
        from apps.auth_portal.routes import auth_bp
        if auth_bp.name not in app.blueprints:
            app.register_blueprint(auth_bp)
        print("✅ [مكون المصادقة]: تم تسجيل موديول auth_portal بنجاح.")
    except Exception as e:
        print(f"❌ [خطأ تسجيل موديول auth_portal]: {e}")
