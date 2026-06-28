# 📂 apps/supplier_wallet/__init__.py

# استيراد الـ Blueprint لتسهيل الوصول إليه عند التسجيل
from .routes import supplier_wallet_bp

# استيراد الخدمات لتسهيل الوصول إليها عند تنفيذ المنطق المالي
from .services import WalletService
