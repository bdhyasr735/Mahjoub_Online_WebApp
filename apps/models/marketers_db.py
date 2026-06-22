# coding: utf-8
from apps import db
from datetime import datetime

class Marketer(db.Model):
    __tablename__ = 'marketers'

    id = db.Column(db.Integer, primary_key=True)
    
    # 1. البيانات الأساسية
    full_name = db.Column(db.String(150), index=True, nullable=False)
    phone = db.Column(db.String(20), index=True) # تواصل
    
    # 2. كود التسويق (مفهرس للبحث السريع عن أداء المسوق)
    marketing_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # 3. الحالة (مفهرس لفلترة المسوقين النشطين)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # 4. إحصائيات للتحمل المليوني (لتقليل الضغط على استعلامات COUNT)
    total_referrals = db.Column(db.Integer, default=0, index=True)
    
    # 5. التوثيق
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Marketer {self.full_name} | Code: {self.marketing_code}>'
