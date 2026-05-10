# 1. الاستيرادات في البداية
import os
import json
import base64
import requests
from datetime import datetime

# 2. استيراد db من النواة (هذا أهم سطر)
from core import db  

# 3. الآن يمكنك تعريف الموديلات
class Supplier(db.Model):
    # كود كلاس Supplier القديم هنا...
    pass

class SupplierStaff(db.Model):
    """
    موديل طاقم الموردين 
    """
    __tablename__ = 'supplier_staff'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(100)) 
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active')
    
    # ربط العلاقة
    supplier = db.relationship('Supplier', backref=db.backref('staff_members', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'phone': self.phone,
            'status': self.status
        }
