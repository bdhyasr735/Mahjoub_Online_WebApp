# coding: utf-8
# 📂 apps/models/otp_db.py

"""
نموذج رموز التحقق (OTP) - للمصادقة الثنائية واستعادة كلمة المرور
"""

from apps.extensions import db
from datetime import datetime, timedelta


class OTP(db.Model):
    """نموذج رموز التحقق المؤقتة"""
    __tablename__ = 'otp_codes'

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(255), nullable=False, index=True)  # البريد أو الجوال
    otp_code = db.Column(db.String(10), nullable=False)  # رمز التحقق
    target_id = db.Column(db.Integer, nullable=False)  # معرف المستخدم
    target_type = db.Column(db.String(50), default='supplier')  # supplier / employee
    expiry = db.Column(db.DateTime, nullable=False)  # وقت الانتهاء
    attempts = db.Column(db.Integer, default=0)  # عدد محاولات الفشل
    is_used = db.Column(db.Boolean, default=False)  # هل تم استخدامه؟
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_valid(self) -> bool:
        """التحقق من صلاحية الرمز"""
        return not self.is_used and datetime.utcnow() < self.expiry

    def increment_attempts(self) -> int:
        """زيادة عدد المحاولات الفاشلة"""
        self.attempts += 1
        db.session.commit()
        return self.attempts

    def mark_used(self):
        """تحديد الرمز كمستخدم"""
        self.is_used = True
        db.session.commit()

    @classmethod
    def create_otp(cls, identifier: str, target_id: int, target_type: str = 'supplier') -> 'OTP':
        """إنشاء رمز تحقق جديد"""
        import secrets
        otp_code = f"{secrets.randbelow(900000) + 100000}"
        expiry = datetime.utcnow() + timedelta(seconds=300)  # 5 دقائق

        otp = cls(
            identifier=identifier,
            otp_code=otp_code,
            target_id=target_id,
            target_type=target_type,
            expiry=expiry
        )
        db.session.add(otp)
        db.session.commit()
        return otp

    @classmethod
    def get_valid_otp(cls, otp_code: str) -> 'OTP':
        """البحث عن رمز تحقق صالح"""
        return cls.query.filter_by(
            otp_code=otp_code,
            is_used=False
        ).first()

    def to_dict(self):
        """تحويل إلى قاموس"""
        return {
            'id': self.id,
            'identifier': self.identifier,
            'otp_code': self.otp_code,
            'target_id': self.target_id,
            'target_type': self.target_type,
            'expiry': self.expiry.isoformat() if self.expiry else None,
            'attempts': self.attempts,
            'is_used': self.is_used,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<OTP {self.otp_code} for {self.identifier}>"
