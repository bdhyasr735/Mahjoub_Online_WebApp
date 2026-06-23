# coding: utf-8
# 📂 apps/suppliers_auth_portal/registry.py - مسجل موديول الموردين والمسوقين في مصنع النظام

import os
from apps.suppliers_auth_portal.routes import suppliers_bp

def register_module(app):
    """
    تسجيل بوابة الموردين والمسوقين السيادية داخل تطبيق Flask الرئيسي.
    يتم استدعاء هذه الدالة ديناميكياً بواسطة الـ System Factory (apps/__init__.py).
    """
    try:
        # تسجيل الـ Blueprint مع تحديد بادئة المسار الافتراضية للبوابة
        # سيصبح مسار الدخول تلقائياً: yourdomain.com/suppliers/login
        app.register_blueprint(suppliers_bp, url_prefix='/suppliers')
        
        print("✅ [Module Registry]: تم تسجيل بوابة الموردين والمسوقين بنجاح (/suppliers)")
        
    except Exception as e:
        print(f"🚨 [Module Registry Error]: فشل تسجيل موديول الموردين: {e}")

# إعدادات الموديول الفنية (Metadata) في حال احتجت لإدارتها ديناميكياً
MODULE_CONFIG = {
    "module_name": "suppliers_auth_portal",
    "version": "2.0.0",
    "auth_type": "OTP & Credentials",
    "secured": True
}
