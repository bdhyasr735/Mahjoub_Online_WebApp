# -*- coding: utf-8 -*-
from flask import Blueprint

# استخدام اسم مميز ومستقل للـ blueprint لكي لا يتكرر مع أي موديول آخر
whatsapp_bp = Blueprint(
    'whatsapp_service_bp', 
    __import__('__main__').__name__,
    template_folder='templates',
    static_folder='static'
)

def register_module(app):
    """تسجيل الموديول في تطبيق فلاسك الرئيسي"""
    from apps.whatsapp_service import routes
    # تسجيل الـ blueprint مع تحديد url_prefix خاص به
    app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
    print("✅ [موديول الواتساب]: تم تسجيل الموديول ومساراته بنجاح.")
