import os
import sys
from datetime import datetime

# --- بروتوكول تثبيت المسارات (Railway Patch) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.extensions import db
except (ImportError, ModuleNotFoundError):
    from ..extensions import db

class Supplier(db.Model):
    """
    نموذج الموردين المطور - منظومة محجوب أونلاين
    يدعم المحفظة الموحدة متعددة العملات والمعرفات المتطابقة
    """
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False) 
    
    owner_name = db.Column(db.String(150), nullable=True)
    trade_name = db.Column(db.String(150), nullable=True)
    activity_type = db.Column(db.String(100), nullable=True) 
    
    tier = db.Column(db.String(50), default='مبتدئ') 
    province = db.Column(db.String(100), nullable=True) 
    district = db.Column(db.String(100), nullable=True) 
    address_detail = db.Column(db.Text, nullable=True) 
    
    id_type = db.Column(db.String(50), nullable=True) 
    id_card_number = db.Column(db.String(50), nullable=True) 
    phone = db.Column(db.String(20), nullable=True) 
    
    # --- النظام المالي الموحد (Multi-Currency Vault) ---
    e_wallet = db.Column(db.String(100), unique=True, nullable=True) # المعرف الموحد WAL_MAH_963...
    
    # أرصدة العملات الثلاث
    balance_yer = db.Column(db.Numeric(20, 2), default=0.00) # ريال يمني
    balance_sar = db.Column(db.Numeric(20, 2), default=0.00) # ريال سعودي
    balance_usd = db.Column(db.Numeric(20, 2), default=0.00) # دولار أمريكي
    
    bank_name = db.Column(db.String(100), nullable=True) 
    bank_acc = db.Column(db.String(100), nullable=True) 
    
    status = db.Column(db.String(20), default='active') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def mint_sovereign_id(self):
        """نقش المعرف السيادي الموحد للمورد ومحفظته"""
        if self.id:
            sovereign_tag = f"963{self.id}"
            self.e_wallet = f"WAL_MAH_{sovereign_tag}"
            return f"SUP_MAH_{sovereign_tag}"
        return None

    def to_dict(self):
        return {
            "id": self.id,
            "trade_name": self.trade_name,
            "owner_name": self.owner_name,
            "phone": self.phone,
            "province": self.province,
            "district": self.district,
            "tier": self.tier,
            "status": self.status,
            "e_wallet": self.e_wallet,
            "balances": {
                "YER": float(self.balance_yer),
                "SAR": float(self.balance_sar),
                "USD": float(self.balance_usd)
            }
        }

    def __repr__(self):
        return f'<Supplier {self.trade_name} | Wallet: {self.e_wallet}>'
