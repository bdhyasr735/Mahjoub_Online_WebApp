models/supplier_db.py

# استيراد الكائن db الموحد من ملف المسؤولين لضمان وحدة قاعدة البيانات

from models.admin_db import db 

from datetime import datetime



class Supplier(db.Model):

    """جدول بيانات الموردين في منظومة محجوب أونلاين"""

    __tablename__ = 'suppliers'

    

    id = db.Column(db.Integer, primary_key=True)

    sovereign_id = db.Column(db.String(50), unique=True) # المعرف السيادي الفريد

    username = db.Column(db.String(50), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    email = db.Column(db.String(100))

    activity_type = db.Column(db.String(50))

    owner_name = db.Column(db.String(150), nullable=False)

    identity_type = db.Column(db.String(50))

    trade_name = db.Column(db.String(150))

    phone = db.Column(db.String(20))

    bank_name = db.Column(db.String(100))

    bank_acc = db.Column(db.String(100))

    province = db.Column(db.String(50))

    district = db.Column(db.String(50))

    address_detail = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)



    def __repr__(self):

        return f'<Supplier {self.trade_name}>'
