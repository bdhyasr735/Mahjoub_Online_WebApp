# coding: utf-8
# 📂 apps/vendors/registry.py - محرك التسجيل التلقائي المعزول لبوابة الموردين

import os

def register_app(app):
    """تسجيل تطبيق الموردين بشكل مستقل وتلقائي داخل مصنع النظام"""
    from apps.vendors.routes import vendors_bp
    
    # تسجيل الـ Blueprint في التطبيق الرئيسي
    app.register_blueprint(vendors_bp)
    
    # تأكيد نجاح الربط في السجلات الداخلية
    print("🚀 [Dynamic Engine] تم دمج وتأمين مسارات بوابة الموردين بنجاح.")
