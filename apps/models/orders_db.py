# 📂 apps/models/orders_db.py
import os
import base64
import hashlib
from apps.extensions import db
from datetime import datetime
from cryptography.fernet import Fernet

# جلب المفتاح المعتمد من متغيرات البيئة
raw_key = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=')

# تهيئة المحرك الأمني
hashed_key = hashlib.sha256(raw_key.encode()).digest()
fernet_key = base64.urlsafe_b64encode(hashed_key)
cipher_suite = Fernet(fernet_key)

class ProcessedOrder(db.Model):
    __tablename__ = 'processed_orders'

    # معرف الطلب من سلة (بدون تشفير ليسهل البحث)
    id = db.Column(db.String(100), primary_key=True) 
    
    # حالة الطلب
    status = db.Column(db.String(50), default='paid')
    
    # الحقل المشفر للقيمة المالية
    _encrypted_total_price = db.Column(db.Text, nullable=False)
    
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def total_price(self):
        """فك تشفير القيمة عند القراءة"""
        try:
            return float(cipher_suite.decrypt(self._encrypted_total_price.encode()).decode())
        except:
            return 0.0

    @total_price.setter
    def total_price(self, value):
        """تشفير القيمة فوراً عند الحفظ"""
        self._encrypted_total_price = cipher_suite.encrypt(str(value).encode()).decode()

    def __repr__(self):
        return f"<ProcessedOrder {self.id}>"
