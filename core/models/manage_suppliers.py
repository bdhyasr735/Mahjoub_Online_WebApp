from core.extensions import db
from datetime import datetime

class SupplierWindow(db.Model):
    __tablename__ = 'supplier_window' # اسم الجدول في القاعدة

    id = db.Column(db.Integer, primary_key=True)
    # الحقول التي تظهر في النافذة (image_86bfc7.png)
    phone = db.Column(db.String(20))
    activity_type = db.Column(db.String(100))
    province = db.Column(db.String(50))
    tier = db.Column(db.String(20), default='مبتدئ')
    status = db.Column(db.String(20), default='نشط')
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
