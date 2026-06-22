# 📂 apps/models/__init__.py

# استيراد النماذج من الملفات المعتمدة
from .admin_db import AdminUser
from .admin_staff_db import AdminStaff

# ⚠️ ملاحظة: إذا كان اسم الكلاس في ملف financials_db.py يختلف، 
# يجب أن يتطابق الاسم المستورد هنا معه تماماً.
from .financials_db import FinancialLog 

from .marketers_db import Marketer
from .orders_db import ProcessedOrder
from .otp_db import OTPVerification
from .supplier_db import Supplier
from .supplier_profile_db import SupplierProfile
from .supplier_staff_db import SupplierStaff
from .sync_log import SyncLog
from .wallet_db import SupplierWallet

__all__ = [
    'AdminUser', 'AdminStaff', 'FinancialLog', 'Marketer', 
    'ProcessedOrder', 'OTPVerification', 'Supplier', 
    'SupplierProfile', 'SupplierStaff', 'SyncLog', 'SupplierWallet'
]
