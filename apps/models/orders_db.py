# coding: utf-8
import os
from datetime import datetime
from cryptography.fernet import Fernet
from apps.extensions import db

# تهيئة آمنة لمفتاح التشفير
def get_cipher():
    key = os.getenv('ENCRYPTION_KEY')
    # إذا لم يوجد مفتاح في البيئة، نستخدم مفتاحاً افتراضياً (للتطوير فقط)
    # في بيئة الإنتاج يجب أن يكون لديك مفتاح ثابت في إعدادات Render
    return Fernet(key.encode()) if key else Fernet(b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=')

cipher = get_cipher()

class Order(db.Model):
    __tablename__ = 'orders'

    # تحسين الأداء: فهارس للبحث السريع عن الطلبات حسب المورد، الحالة، أو المرجع
    __table_args__ = (
        db.Index('idx_ord_supplier_id', 'supplier_id'),
        db.Index('idx_ord_ref', 'order_reference'),
        db.Index('idx_ord_status', 'status'),
        db.Index('idx_ord_created', 'created_at'),
        {'extend_existing': True}
    )

    # المعرفات الأساسية
    id = db.Column(db.String(100), primary_key=True) 
    order_id_display = db.Column(db.String(50), nullable=True)
    
    # الربط السيادي
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    order_reference = db.Column(db.String(100), unique=True, nullable=True) 
    
    # بيانات ظاهرة (بدون تشفير) للتقارير والفلترة المالية السريعة
    total_price = db.Column(db.Numeric(18, 2), default=0.00)
    items_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(30), default='pending') 
    
    # بيانات مشفرة (لحماية خصوصية العميل)
    _customer_name = db.Column(db.Text)
    _customer_phone = db.Column(db.Text)
    _customer_address = db.Column(db.Text)
    
    # التوثيق الزمني
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    supplier = db.relationship('Supplier', back_populates='orders')
    financials = db.relationship('OrderFinancial', back_populates='order', uselist=False, cascade="all, delete-orphan")

    # --- منطق التشفير الاحترافي ---
    
    @property
    def customer_name(self):
        if not self._customer_name: return "غير معروف"
        try: return cipher.decrypt(self._customer_name.encode()).decode()
        except: return "خطأ في التشفير"

    @customer_name.setter
    def customer_name(self, value):
        self._customer_name = cipher.encrypt(str(value).encode()).decode()

    @property
    def customer_phone(self):
        try: return cipher.decrypt(self._customer_phone.encode()).decode() if self._customer_phone else None
        except: return None

    @customer_phone.setter
    def customer_phone(self, value):
        if value: self._customer_phone = cipher.encrypt(str(value).encode()).decode()

    @property
    def customer_address(self):
        try: return cipher.decrypt(self._customer_address.encode()).decode() if self._customer_address else None
        except: return None

    @customer_address.setter
    def customer_address(self, value):
        if value: self._customer_address = cipher.encrypt(str(value).encode()).decode()

    def __repr__(self):
        return f'<Order {self.order_id_display or self.id} | Status: {self.status}>'
