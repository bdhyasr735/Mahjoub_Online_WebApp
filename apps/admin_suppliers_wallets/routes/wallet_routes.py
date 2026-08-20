# coding: utf-8
"""
📂 apps/admin_suppliers_wallets/routes/wallet_routes.py
متحكم محفظة المورد الرئيسي (Supplier Wallet Flask Controller)
- عرض كشف الحساب وسندات الحركات المالية مع البحث المفهرس
- تقديم طلبات السحب المالي عبر POST المباشر (Zero-JS)
- إرسال التنبيهات الفورية (Toasts)
"""

from decimal import Decimal
from flask import render_template, request, redirect, url_for, g
from models.wallet_models import (
    SupplierWallet,
    WalletTransaction,
    WithdrawalRequest,
    VoucherReceipt
)
from models.bank_account_models import BankAccount
# ✅ تصحيح مسارات استيراد الخدمات لتطابق المجلد الحالي
from apps.admin_suppliers_wallets.services.wallet_service import WalletService
from apps.admin_suppliers_wallets.services.notification_service import NotificationService
# ملاحظة: يتم استدعاء الـ blueprint الخاص بالمجلد الحالي أو تعريفه محلياً حسب ملف __init__.py
