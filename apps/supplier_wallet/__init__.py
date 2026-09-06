# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/__init__.py

from .routes import supplier_wallet_bp

def init_app(app):
    """
    دالة تهيئة حزمة المحفظة وتسجيل الـ Blueprint في تطبيق Flask الرئيسي.
    """
    app.register_blueprint(supplier_wallet_bp)

def register_module(app):
    """
    دالة متوافقة مع نظام التسجيل الديناميكي للموديولات.
    """
    init_app(app)
