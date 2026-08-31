# -*- coding: utf-8 -*-
# 📂 apps/auth_portal/registry.py

from flask import Blueprint

MODULE_NAME = "بوابة المصادقة الإدارية"
MODULE_ICON = "fa-shield-alt"
SHOW_IN_SUPPLIER = False

NAV_ITEMS = [
    # يمكن إضافة روابط القائمة الجانبية الإدارية الخاصة بالمصادقة هنا إن وجدت
]

def register_module(app):
    """تسجيل مودي وبوابات المصادقة الإدارية"""
    try:
        from apps.auth_portal.routes import auth_bp
        if auth_bp.name not in app.blueprints:
            app.register_blueprint(auth_bp)
        print("✅ [مجلد auth_portal]: تم تسجيل الموديول وبواباته بنجاح.")
    except ImportError as e:
        print(f"⚠️ [تحذير موديول auth_portal]: لم يتم العثور على المسارات: {e}")
    except Exception as e:
        print(f"❌ [خطأ موديول auth_portal]: فشل التسجيل: {e}")
