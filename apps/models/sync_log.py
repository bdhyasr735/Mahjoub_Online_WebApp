# 📂 apps/models/sync_log.py
from apps.extensions import db
from datetime import datetime

class SyncLog(db.Model):
    __tablename__ = 'sync_logs'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(100), index=True) # رقم الطلب للبحث السريع
    status = db.Column(db.String(20)) # (success, failed)
    message = db.Column(db.Text) # وصف ما حدث
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SyncLog {self.order_id} - {self.status}>"
