# coding: utf-8
# 📂 apps/models/__init__.py

"""
مركز التحكم في الموديلات (Model Registry) - محدث ومدمج مع سجل الخزينة المركزية ونماذج الواتساب
"""

from apps.extensions import db

from apps.models.supplier_db import Supplier
from apps.models.admin_db import AdminUser
from apps.models.marketer_db import Marketer
from apps.models.admin_staff_db import AdminStaff
from apps.models.supplier_profile_db import SupplierProfile
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.financials_db import OrderFinancial
from apps.models.treasury_db import TreasuryEntry
from apps.models.orders_db import Order
from apps.models.order_items_db import OrderItem
from apps.models.product_db import Product
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.sync_log import SyncLog

# استيراد نماذج الواتساب بشكل صحيح ودون مشاكل في مسارات الاستيراد
from apps.models.whatsapp_models import (
    WhatsAppMessageLog,
    WhatsAppWebhookEvent,
    WhatsAppCustomerContact
)

__all__ = [
    'db',
    'AdminStaff',
    'AdminUser',
    'Marketer',
    'Order',
    'OrderFinancial',
    'OrderItem',
    'Product',
    'ProductSupplierMapping',
    'Supplier',
    'SupplierProfile',
    'SupplierStaff',
    'SupplierWallet',
    'TreasuryEntry',
    'SyncLog',
    'WalletTransaction',
    'WhatsAppMessageLog',
    'WhatsAppWebhookEvent',
    'WhatsAppCustomerContact'
]