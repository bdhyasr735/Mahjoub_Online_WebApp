# coding: utf-8
from apps.extensions import db
from apps.utils.security import AESCipher

class ProcessedOrder(db.Model):
    __tablename__ = 'processed_orders'
    
    id = db.Column(db.String(100), primary_key=True)
    order_id = db.Column(db.String(50))
    
    # حقول مشفرة (استخدام النمط الذي أرسلته)
    _total_price = db.Column('total_price', db.String(255))
    _customer_name = db.Column('customer_name', db.String(255))
    _customer_phone = db.Column('customer_phone', db.String(255))
    _customer_email = db.Column('customer_email', db.String(255))
    
    # حقول غير مشفرة (حسب حاجتك)
    order_status = db.Column(db.String(50))
    shipping_city = db.Column(db.String(100))
    shipping_street = db.Column(db.String(200))

    # --- Property للحقول المشفرة ---
    @property
    def total_price(self):
        val = AESCipher.decrypt(self._total_price)
        return float(val) if val else 0.0
    
    @total_price.setter
    def total_price(self, value):
        self._total_price = AESCipher.encrypt(str(value))

    @property
    def customer_name(self):
        return AESCipher.decrypt(self._customer_name)
    
    @customer_name.setter
    def customer_name(self, value):
        self._customer_name = AESCipher.encrypt(str(value))

    @property
    def customer_phone(self):
        return AESCipher.decrypt(self._customer_phone)
    
    @customer_phone.setter
    def customer_phone(self, value):
        self._customer_phone = AESCipher.encrypt(str(value))
