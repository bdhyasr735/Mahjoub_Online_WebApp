# -*- coding: utf-8 -*-
"""
ملف تسجيل موديول محفظة المورد (Supplier Wallet Registry)
مسؤول عن تسجيل الموديول والـ Blueprints بداخل تطبيق Flask الأساسي.
Mahjoub Online WebApp - supplier_wallet/registry.py
"""

import os
from flask import Blueprint

# تحديد المجلدات الخاصة بالقوالب والمستندات الثابتة للموديول
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

# إنشاء Blueprint لموديول المحفظة مع بادئة الرابط /supplier
wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder=TEMPLATE_DIR,
    url_prefix='/supplier'
)

def register_module(app):
    """
    دالة تسجيل الموديول في تطبيق Flask الرئيسي.
    تستورد المسارات وتمرر الـ Blueprint للتطبيق.
    """
    # استيراد المسارات لربطها بـ Blueprint عند التسجيل
    from .routes import wallet_routes

    # تسجيل الـ Blueprint بداخل تطبيق Flask
    app.register_blueprint(wallet_bp)

    # إضافة سياق عمومي للقوالب إذا لزم الأمر (مثل أسماء العملة والرموز)
    @app.context_processor
    def inject_wallet_defaults():
        return {
            'CURRENCY_SYMBOL': 'ج.م',
            'WALLET_MODULE_NAME': 'محفظة المورد'
        }

    print(" Successfully registered [supplier_wallet] module blueprints.")
