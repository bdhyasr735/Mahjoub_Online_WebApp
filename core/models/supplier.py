# core/models/supplier.py
import os
import json
import base64
import requests
from datetime import datetime
from core import db

class Supplier(db.Model):
    """
    موديل المورد السيادي - قاعدة البيانات المركزية لترسانة محجوب أونلاين
    """
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    sovereign_id = db.Column(db.String(50), unique=True) # مثال: SUP_101#
    trade_name = db.Column(db.String(150), nullable=False)
    owner_name = db.Column(db.String(150))
    province = db.Column(db.String(100)) # المحافظة
    district = db.Column(db.String(100)) # المديرية
    phone = db.Column(db.String(20))
    tier = db.Column(db.String(50), default='مبتدئ') # (سيادي، ذهبي، مبتدئ)
    
    # سجلات الأرصدة المتعددة (المحفظة الثلاثية)
    balance_yer = db.Column(db.Float, default=0.0)
    balance_sar = db.Column(db.Float, default=0.0)
    balance_usd = db.Column(db.Float, default=0.0)
    
    status = db.Column(db.String(20), default='active') 
    staff_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """تحويل البيانات إلى JSON لتغذية لوحة القيادة"""
        return {
            'id': self.id,
            'sovereign_id': self.sovereign_id or f"SUP_{self.id}#",
            'trade_name': self.trade_name,
            'owner_name': self.owner_name,
            'province': self.province,
            'tier': self.tier,
            'balance_yer': self.balance_yer,
            'balance_sar': self.balance_sar,
            'balance_usd': self.balance_usd,
            'status': self.status,
            'staff_count': self.staff_count
        }

class SupplierStaff(db.Model):
    """ موديل طاقم الموردين - يتبع نافذة الموردين """
    __tablename__ = 'supplier_staff'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(100)) # مدير، محاسب، مندوب
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active')
    
    # ربط العلاقة العكسية
    supplier = db.relationship('Supplier', backref=db.backref('staff_members', lazy=True))

class ArchiveManager:
    """ نظام الأرشفة السيادية لتوثيق العمليات على GitHub """
    def __init__(self):
        # التوكن يتم جلبه من متغيرات البيئة لزيادة الأمان
        self.github_token = os.getenv("GITHUB_TOKEN", "your_private_token_here")
        self.repo_name = "Mahjoub-Online-Archive" 
        self.username = "Ali-Mahjoub" 
        self.base_url = f"https://api.github.com/repos/{self.username}/{self.repo_name}/contents/"

    def archive_entity(self, entity_obj):
        """ أرشفة بيانات كيان كامل (مورد مثلاً) إلى GitHub فوراً """
        if not self.github_token: return False
        
        data = entity_obj.to_dict()
        filename = f"{data['trade_name']}_{datetime.now().strftime('%Y%m%d')}"
        path = f"Archives/Suppliers/{data['sovereign_id']}/{filename}.json"
        
        content = json.dumps(data, indent=4, ensure_ascii=False)
        encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')

        payload = {"message": f"Sovereign Archive: {data['sovereign_id']}", "content": encoded}
        headers = {"Authorization": f"token {self.github_token}", "Accept": "application/vnd.github.v3+json"}

        try:
            requests.put(self.base_url + path, headers=headers, json=payload, timeout=10)
            return True
        except:
            return False

# تشغيل محرك الأرشفة
archive_sys = ArchiveManager()
