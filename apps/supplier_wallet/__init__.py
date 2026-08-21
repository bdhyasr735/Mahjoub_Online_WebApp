# -*- coding: utf-8 -*-
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from apps.extensions import db

# استيراد آمن لنماذج قاعدة بيانات المحفظة لمنع أي خطأ استيراد
try:
    from apps.models.wallet_db import SupplierWallet
except ImportError:
    SupplierWallet = None

try:
    from apps.models.wallet_db import WalletTransaction
except ImportError:
    WalletTransaction = None

from apps.supplier_wallet.services.wallet_service import WalletService
from apps.supplier_wallet.services.notification_service import NotificationService
from apps.supplier_wallet.utils import get_current_supplier_id

# استيراد البيانات مباشرة من ملفات الداتا
from apps.data.yemen_banks import YEMEN_BANKS
from apps.data.financial_companies import FINANCIAL_COMPANIES

supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static'
)
