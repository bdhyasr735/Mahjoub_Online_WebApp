"""
audit_logger.py
خدمة تدقيق وتتبع العمليات الإدارية (Audit Logging Service)
لمراقبة وتوثيق كافة الأنشطة والتعديلات التي يتم إجراؤها في لوحة تحكم محجوب أونلاين.
"""

import logging
from datetime import datetime
from flask import request, session, g
from apps import db

logger = logging.getLogger(__name__)

class AuditLog(db.Model):
    """
    نموذج جدول سجلات التدقيق في قاعدة البيانات.
    """
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)          # معرّف المشرف أو المستخدم الذي قام بالعملية
    username = db.Column(db.String(100), nullable=True)     # اسم المشرف
    action = db.Column(db.String(100), nullable=False)      # نوع الحدث أو العملية (مثل: UPDATE_STATUS, MAP_SUPPLIER)
    target_type = db.Column(db.String(50), nullable=True)   # نوع الهدف (مثل: Order, Supplier, Product)
    target_id = db.Column(db.String(100), nullable=True)    # معرّف العنصر المستهدف (Order ID أو QID)
    details = db.Column(db.Text, nullable=True)             # تفاصيل إضافية أو وصف للعملية
    ip_address = db.Column(db.String(50), nullable=True)    # عنوان الـ IP الخاص بالمشرف لأسباب أمنية
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # وقت حدوث العملية

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.username} at {self.created_at}>"


class AuditLogger:
    """
    متحكم عمليات التسجيل لتسهيل استدعائها في أي مكان بالمنصة.
    """
    
    @staticmethod
    def log(action, target_type=None, target_id=None, details=None):
        """
        دالة أساسية لتسجيل أي حدث جديد في النظام حفظاً للشفافية والمراجعة.
        
        :param action: وصف موجز للعملية (مثال: 'UPDATE_ORDER_STATUS', 'MAP_LOCAL_SUPPLIER')
        :param target_type: نوع الكائن المتأثر (مثال: 'Order', 'Product')
        :param target_id: معرّف الكائن (مثال: معرّف الطلب أو الـ QID)
        :param details: تفاصيل نصية أو وصف إضافي للتغيير الذي حدث
        """
        try:
            # محاولة جلب بيانات المشرف الحالي من الجلسة أو السياق العام
            user_id = session.get('user_id') or getattr(g, 'user_id', None)
            username = session.get('username') or getattr(g, 'username', 'Admin / System')
            
            # التقاط عنوان الـ IP للطلب إن وجد
            ip_addr = request.remote_addr if request else None

            # إنشاء سجل التدقيق الجديد
            log_entry = AuditLog(
                user_id=user_id,
                username=username,
                action=action,
                target_type=target_type,
                target_id=str(target_id) if target_id else None,
                details=details,
                ip_address=ip_addr
            )
            
            db.session.add(log_entry)
            db.session.commit()
            
            logger.info(f"Audit Log Recorded: [{action}] on {target_type}:{target_id} by {username}")
            return True

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to record audit log [{action}]: {e}")
            return False
