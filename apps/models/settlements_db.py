# coding: utf-8
# 📂 apps/models/settlements_db.py
# 📜 مستند حوكمة إدارة التسويات المالية الاستثنائية والسندات الإدارية - منصة محجوب أونلاين 2026
# تم تعديل الاستيراد من apps.extensions لكسر حلقة Circular Import

import random
from datetime import datetime
from apps.extensions import db

class AdminSettlement(db.Model):
    """
    جدول مخصص مستقل حصرياً لإدارة وتوثيق التسويات المالية الإدارية والاستثنائية.
    يعمل كجدول مخصص مغذّي لنوافذ التسويات والرقابة المادية في لوحة التحكم المركزية.
    """
    __tablename__ = 'admin_settlements'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # الربط الحوكمي مع ملف الأب (SupplierWallet)
    wallet_id = db.Column(db.Integer, db.ForeignKey('supplier_wallets.id'), nullable=False)
    wallet_code = db.Column(db.String(50), nullable=False) # لسهولة الاستعلام المباشر والسريع من النافذة
    
    # تفاصيل السند المالي للحركة
    settlement_code = db.Column(db.String(60), unique=True, nullable=False) # رمز السند المالي (STL-...)
    settlement_type = db.Column(db.String(30), nullable=False)             # إيداع شحن / خصم عكسي / تسوية غرامة
    currency = db.Column(db.String(10), nullable=False)                    # YER / SAR / USD
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # توثيق التدقيق البنكي والربط الخارجي الصادر
    financial_entity = db.Column(db.String(100), default="إدارة المنصة المركزية", nullable=True) # اسم الجهة أو الصراف
    reference_number = db.Column(db.String(100), default="SETTLE-ADMIN", nullable=True)          # رقم السند المرجعي أو الحوالة
    
    # حوكمة وضبط الصلاحيات البشرية لمنع التلاعب بالمدخلات
    reason_notes = db.Column(db.Text, nullable=False)  # بيان السبب الإجباري لفرض القيد والتسوية
    created_by = db.Column(db.String(50), nullable=True) # هوية المسؤول أو الإداري الذي قام بالعملية
    
    status = db.Column(db.String(20), default='منفذة', nullable=False) # منفذة / ملغاة
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @staticmethod
    def generate_settlement_code():
        """ 📊 محرك التوليد الآلي والمشفر لرموز سندات التسوية الإدارية لعام 2026 """
        return f"STL-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"

    def __repr__(self):
        return f"<AdminSettlement {self.settlement_code} | Wallet {self.wallet_code} | {self.amount} {self.currency}>"
