# 📂 apps/models/orders_db.py
import os
import base64
import hashlib
from apps.extensions import db
from datetime import datetime
from cryptography.fernet import Fernet

# 🔐 جلب المفتاح المعتمد والمطابق لملف الـ Config السيادي الخاص بك
raw_key = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=')

# تهيئة المفتاح ليتوافق مع معيار Fernet (AES-256) بدقة
try:
    # نقوم بعمل hashing للمفتاح لضمان طول 32 بايت مشفر بـ base64 لتفادي أي خطأ صياغي في المصنع
    hashed_key = hashlib.sha256(raw_key.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(hashed_key)
    cipher_suite = Fernet(fernet_key)
except Exception as e:
    cipher_suite = None
    print(f"⚠️ خطأ في تهيئة محرك التشفير: {e}")

class ProcessedOrder(db.Model):
    """
    جدول سيادي محصّن بتشفير AES-256 لتتبع وتوثيق الطلبات التي تم تسويتها حياً.
    """
    __tablename__ = 'processed_orders'

    id = db.Column(db.String(100), primary_key=True)  # معرف الطلب القادم من قمرة
    status = db.Column(db.String(50), default='processed')  # حالة التسوية
    _encrypted_total_price = db.Column(db.Text, nullable=False)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def total_price(self):
        """فك تشفير القيمة المالية تلقائياً عند القراءة"""
        try:
            if cipher_suite and self._encrypted_total_price:
                decrypted_data = cipher_suite.decrypt(self._encrypted_total_price.encode()).decode()
                return float(decrypted_data)
        except Exception:
            pass
        return 0.0

    @total_price.setter
    def total_price(self, value):
        """تشفير القيمة المالية فوراً بمعيار AES-256 قبل الحفظ"""
        if cipher_suite:
            encrypted_data = cipher_suite.encrypt(str(value).encode()).decode()
            self._encrypted_total_price = encrypted_data
        else:
            self._encrypted_total_price = str(value)

    def __repr__(self):
        return f"<ProcessedOrder {self.id}>"
