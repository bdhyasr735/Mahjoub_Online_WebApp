# 📂 apps/models/__init__.py
# الفهرس الموحد لجميع موديلات قاعدة البيانات (مرتب بدقة لمنع فشل الـ Mapper)

# 1. الموديلات المستقلة تماماً (الأبناء/المكونات الأساسية)
from .admin_db import AdminUser
from .admin_staff_db import AdminStaff
from .marketers_db import Marketer
from .otp_db import OTPVerification
from .sync_log import SyncLog

# 2. الموديلات التي تُعتمد عليها (يجب استيرادها قبل الموديلات التي تربط بها)
from .supplier_profile_db import SupplierProfile 
from .supplier_staff_db import SupplierStaff
from .wallet_db import VendorWallet 

# 3. الموديلات الرئيسية (التي تحتوي على الـ relationships)
from .supplier_db import Supplier
from .orders_db import Order
from .financials_db import OrderFinancial 

# القائمة الموحدة للتصدير
__all__ = [
    'Supplier', 'AdminUser', 'AdminStaff', 'Marketer', 
    'OTPVerification', 'SupplierProfile', 'SupplierStaff', 
    'SyncLog', 'VendorWallet', 'Order', 'OrderFinancial'
]
