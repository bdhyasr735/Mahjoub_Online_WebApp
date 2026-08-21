from apps.models.wallet_db import (
    SupplierWallet,
    WalletTransaction,
    WithdrawalRequest,
    WalletAuditLog,
    generate_voucher_number,
    get_mecca_now
)

# استيراد آمن لكلاس السندات لضمان عدم توقف السيرفر
try:
    from apps.models.wallet_db import VoucherReceipt
except ImportError:
    VoucherReceipt = None
