# coding: utf-8
# 📂 apps/supplier_wallet/__init__.py
"""
Mahjoub Online WebApp - Supplier Wallet Module
Package initialization for apps/supplier_wallet
"""
from .registry import supplier_wallet_bp, register_module

# استيراد ملفات المسارات لضمان تسجيل الـ Routes وربطها بالـ Blueprint
from apps.supplier_wallet import wallet_routes, withdraw_routes, export_routes

__all__ = ['supplier_wallet_bp', 'register_module']
