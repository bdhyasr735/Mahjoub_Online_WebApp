# coding: utf-8
# 🔑 مستند تهيئة حزمة العمليات المالية والمحافظ - منصة محجوب أونلاين 2026

from flask import Blueprint
from apps import db # استيراد كائن قاعدة البيانات المركزي

# إنشاء البلوبرينت المعزول والمستقل لإدارة الحوكمة المالية والمحافظ
admin_wallet = Blueprint(
    'admin_wallet', 
    __name__, 
    template_folder='templates',
    url_prefix='/admin/wallet'
)

# 🚀 حقن محرك الإنشاء التلقائي للجداول المفقودة عند الإقلاع الأول
@admin_wallet.before_app_request
def create_wallet_tables_once():
    try:
        # استيراد الموديلات هنا للتأكد من أن SQLAlchemy يراها ويقوم بإنشائها
        from apps.models.wallet_db import Wallet, WalletTransaction
        
        # أمر سيادي لإنشاء الجداول المفقودة في Postgres فوراً دون المساس بالبيانات القديمة
        db.create_all()
    except Exception as e:
        print(f"⚠️ تنبيه حوكمي أثناء إنشاء جداول المحافظ: {str(e)}")

# استيراد المسارات بعد تعريف البلوبرينت لحمايتها من التداخل
from . import routes
