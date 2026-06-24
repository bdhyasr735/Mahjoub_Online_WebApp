# coding: utf-8
# 📂 apps/suppliers_auth_portal/registry.py - مسجل موديول الموردين والمسوقين

import os
from apps.suppliers_auth_portal.routes import suppliers_bp

def register_module(app):
    """
    تسجيل بوابة الموردين والمسوقين السيادية داخل تطبيق Flask الرئيسي.
    تلقائياً يتم تسجيل المسارات التالية:
    - /suppliers/login
    - /suppliers/verify
    - /suppliers/dashboard
    """
    try:
        # تسجيل الـ Blueprint
        app.register_blueprint(suppliers_bp, url_prefix='/suppliers')
        
        print("✅ [Module Registry]: تم تسجيل بوابة الموردين (بما في ذلك نافذة التحقق) بنجاح (/suppliers)")
        
    except Exception as e:
        print(f"🚨 [Module Registry Error]: فشل تسجيل موديول الموردين: {e}")

# إعدادات الموديول الفنية
MODULE_CONFIG = {
    "module_name": "suppliers_auth_portal",
    "version": "2.0.0",
    "auth_type": "OTP & Credentials",
    "secured": True
}
