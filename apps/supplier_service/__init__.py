# -*- coding: utf-8 -*-
from flask import Blueprint

MODULE_NAME = "إدارة خدمات الموردين"
MODULE_ICON = "fa-truck-loading"
SHOW_IN_SUPPLIER = True  # أو False حسب ما إذا كان يظهر للموردين أو للإدارة

NAV_ITEMS = [
    # حدد الروابط التي ستظهر في القائمة الجانبية هنا
    # {'endpoint': 'supplier_service.index', 'title': 'قائمة الخدمات'}
]

def register_module(app):
    from apps.supplier_service.routes import supplier_service_bp
    app.register_blueprint(supplier_service_bp, url_prefix='/supplier')
    print("✅ [موديول خدمات الموردين]: تم تسجيله بنجاح عبر الـ registry.")
