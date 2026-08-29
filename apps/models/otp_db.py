# coding: utf-8
from apps.extensions import db
from datetime import datetime, timedelta
import hashlib
import secrets
import hmac
import os


class OTP(db.Model):
    __tablename__ = 'otp_codes'

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(255), nullable=False, index=True)
    otp_hash = db.Column(db.String(128), nullable=False)
    otp_salt = db.Column(db.String(64), nullable=False)
    target_id = db.Column(db.Integer, nullable=False, index=True)
    target_type = db.Column(db.String(50), default='supplier')
    expiry = db.Column(db.DateTime, nullable=False, index=True)
    attempts = db.Column(db.Integer, default=0)
    max_attempts = db.Column(db.Integer, default=5)
    is_used = db.Column(db.Boolean, default=False, index=True)
    is_blocked = db.Column(db.Boolean, default=False)
    blocked_until = db.Column(db.DateTime, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def _hash_otp(otp_code: str, salt: str = None) -> tuple:
        if salt is None:
            salt = os.urandom(16).hex()
        key = hashlib.pbkdf2_hmac(
            'sha256',
            otp_code.encode('utf-8'),
            salt.encode('utf-8'),
            iterations=100000
        )
        return key.hex(), salt

    @staticmethod
    def _verify_otp(otp_code: str, stored_hash: str, salt: str) -> bool:
        computed_hash, _ = OTP._hash_otp(otp_code, salt)
        return hmac.compare_digest(computed_hash, stored_hash)

    @classmethod
    def create_otp(cls, identifier: str, target_id: int, target_type: str = 'supplier',
                   ip_address: str = None, user_agent: str = None, expiry_seconds: int = 300):
        otp_code = f"{secrets.randbelow(900000) + 100000}"
        otp_hash, otp_salt = cls._hash_otp(otp_code)
        expiry = datetime.utcnow() + timedelta(seconds=expiry_seconds)

        otp = cls(
            identifier=identifier,
            otp_hash=otp_hash,
            otp_salt=otp_salt,
            target_id=target_id,
            target_type=target_type,
            expiry=expiry,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(otp)
        db.session.commit()
        return otp, otp_code

    def verify(self, otp_code: str) -> dict:
        if self.is_used:
            return {'success': False, 'message': 'تم استخدام هذا الرمز مسبقاً'}

        if self.is_blocked and self.blocked_until and datetime.utcnow() < self.blocked_until:
            remaining = int((self.blocked_until - datetime.utcnow()).total_seconds())
            return {'success': False, 'message': f'محظور مؤقتاً، انتظر {remaining} ثانية'}

        if datetime.utcnow() > self.expiry:
            return {'success': False, 'message': 'انتهت صلاحية الرمز'}

        if self.attempts >= self.max_attempts:
            self.is_blocked = True
            self.blocked_until = datetime.utcnow() + timedelta(minutes=15)
            db.session.commit()
            return {'success': False, 'message': 'تم تجاوز المحاولات، محظور 15 دقيقة'}

        if not self._verify_otp(otp_code, self.otp_hash, self.otp_salt):
            self.attempts += 1
            db.session.commit()
            return {'success': False, 'message': f'رمز غير صحيح، تبقى {self.max_attempts - self.attempts} محاولات'}

        self.is_used = True
        db.session.commit()
        return {'success': True, 'message': 'تم التحقق بنجاح'}

    @classmethod
    def get_valid_otp(cls, otp_code: str, identifier: str = None):
        query = cls.query.filter(
            cls.is_used == False,
            cls.is_blocked == False,
            cls.expiry > datetime.utcnow()
        )
        if identifier:
            query = query.filter(cls.identifier == identifier)
        valid_otps = query.all()
        for otp in valid_otps:
            if otp._verify_otp(otp_code, otp.otp_hash, otp.otp_salt):
                return otp
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'identifier': self.identifier,
            'target_id': self.target_id,
            'target_type': self.target_type,
            'expiry': self.expiry.isoformat() if self.expiry else None,
            'is_used': self.is_used,
            'is_blocked': self.is_blocked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
