# coding: utf-8
# 📂 apps/models/sync_log.py

from datetime import datetime
from apps.extensions import db
from apps.utils.security import AESCipher

class SyncLog(db.Model):
    """سجل العمليات (SyncLog): لتعقب كافة عمليات المزامنة والربط مع الموردين."""
    __tablename__ = 'sync_logs'
    
    # المعرف الأساسي
    id = db.Column(db.Integer, primary_key=True)
    
    # 🔗 الربط مع المورد والطلب لتعقب المشاكل بدقة
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True, index=True)
    order_id = db.Column(db.String(100), nullable=True, index=True) 
    
    # ⚡ معلومات العملية
    sync_type = db.Column(db.String(50), nullable=False, index=True) # (orders, inventory, etc.)
    status = db.Column(db.String(20), nullable=False, index=True)    # (success, failed)
    
    # 🔐 تشفير رسالة الخطأ (لحماية البيانات الحساسة داخل سجلات الخطأ)
    _error_message = db.Column('error_message', db.Text, nullable=True)
    
    # ⚡ الفهرسة للبحث الزمني
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # --- منطق التشفير السيادي ---
    @property
    def error_message(self):
        """فك تشفير رسالة الخطأ عند القراءة"""
        if not self._error_message:
            return None
        try:
            return AESCipher.decrypt(self._error_message)
        except Exception:
            return "تعذر فك تشفير السجل"

    @error_message.setter
    def error_message(self, value):
        """تشفير رسالة الخطأ قبل الحفظ"""
        if value:
            self._error_message = AESCipher.encrypt(str(value))
        else:
            self._error_message = None

    def __repr__(self):
        return f'<SyncLog {self.sync_type} | Status: {self.status} | Time: {self.timestamp}>'
