# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/__init__.py

from .routes import supplier_wallet_bp

def register_module(app):
    """
    هذه هي الدالة التي يبحث عنها النظام الديناميكي لتسجيل الموديول.
    """
    if 'supplier_wallet_bp' not in app.blueprints:
        app.register_blueprint(supplier_wallet_bp)

def init_app(app):
    register_module(app)
