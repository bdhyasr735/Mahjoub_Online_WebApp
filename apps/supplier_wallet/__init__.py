# coding: utf-8
# 📂 apps/supplier_wallet/__init__.py
"""
Mahjoub Online WebApp - Supplier Wallet Module
Package initialization for apps/supplier_wallet
"""
from .registry import supplier_wallet_bp, register_module

# ✅ استيراد ملف المسارات الرئيسي فقط (يحتوي على كل الوظائف: dashboard, withdraw, export-pdf)
from apps.supplier_wallet import wallet_routes

# ❌ تم إزالة withdraw_routes و export_routes لتجنب تضارب نقاط النهاية (endpoint) 
#    حيث أن wallet_routes.py يغطي جميع المسارات المطلوبة بشكل كامل وآمن.

__all__ = ['supplier_wallet_bp', 'register_module']
