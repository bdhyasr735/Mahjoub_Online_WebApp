# coding: utf-8
# 💳 مستند النموذج الحوكمي للمحافظ الموحدة - منصة محجوب أونلاين 2026

import random
from datetime import datetime
from apps import db

class SupplierWallet(db.Model):
    __tablename__ = 'supplier_wallets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    supplier_id = db.Column(db.String(50), db.ForeignKey('suppliers.sovereign_id'), nullable=False, unique=True)
    wallet_code = db.Column(db.String(50), nullable=False, unique=True)
    
    # الأعمدة الفعلية الحية للمنظومة المالية الموحدة
    yer_total = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)
    yer_withdrawn = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)
    yer_pending = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)

    sar_total = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)
    sar_withdrawn = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)
    sar_pending = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)

    usd_total = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)
    usd_withdrawn = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)
    usd_pending = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)

    status = db.Column(db.String(20), default='نشطة', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 📊 محرك التوليد التلقائي لرموز المحافظ متناسق هندسياً مع الموردين
    @staticmethod
    def generate_next_wallet_code():
        """ استعلام مباشر لجلب معرف المحفظة التالي متناسقاً مع الجدول الحي """
        last_wallet = SupplierWallet.query.order_by(SupplierWallet.id.desc()).first()
        if last_wallet and last_wallet.wallet_code:
            try:
                parts = last_wallet.wallet_code.split('MAH963')
                last_num = int(parts[-1])
                return f"WEL-MAH963{last_num + 1}"
            except (ValueError, IndexError):
                return f"WEL-MAH963{random.randint(100, 999)}"
        return "WEL-MAH9631"

    def __repr__(self):
        return f"<SupplierWallet {self.wallet_code}>"
