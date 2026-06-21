# coding: utf-8
# 📂 apps/models/otp_db.py - نظام إدارة الرموز السيادي (مؤمن ومفهرس للسرعة القصوى)

import random
from apps.extensions import db
from apps.utils.security import AESCipher
from datetime import datetime, timedelta

class OTPVerification(db.Model):
    __tablename__ = 'otp_verifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # ⚡ فهرسة user_identifier ضرورية جداً للوصول للرمز الخاص بالمستخدم بسرعة
    user_identifier = db.Column(db.String(150), index=True, nullable=False)
    
    # 🔐 تخزين الرمز مشفراً (تم تأمين الـ Column)
    _otp_code_enc = db.Column('otp_code', db.String(255), nullable=False)
    
    # ⚡ فهرسة is_used و expires_at لتسريع الاستعلام عن الرموز الفعالة فقط
    is_used = db.Column(db.Boolean, default=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    @property
    def otp_code(self):
        try:
            return AESCipher.decrypt(self._otp_code_enc) if self._otp_code_enc else None
        except Exception:
            return None

    @otp_code.setter
    def otp_code(self, value):
        self._otp_code_enc = AESCipher.encrypt(str(value)) if value else None

    @staticmethod
    def generate_otp(identifier, expires_in_minutes=5):
        """توليد رمز جديد وإبطال أي رموز سابقة لنفس المستخدم"""
        try:
            # ⚡ الفهرسة تجعل هذا التحديث فورياً حتى مع وجود ملايين الرموز السابقة
            OTPVerification.query.filter_by(user_identifier=identifier, is_used=False).update({"is_used": True})
            
            raw_code = str(random.randint(100000, 999999))
            
            new_otp = OTPVerification(
                user_identifier=identifier,
                expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes),
                otp_code=raw_code 
            )
            db.session.add(new_otp)
            db.session.commit()
            return raw_code
        except Exception as e:
            db.session.rollback()
            return None

    @staticmethod
    def verify_otp(identifier, input_code):
        """التحقق من صحة الرمز واستهلاكه فوراً (مفهرس للسرعة)"""
        try:
            now = datetime.utcnow()
            # ⚡ البحث هنا يستخدم فهارس (user_identifier, is_used) مما يمنع بطء الاستعلام
            otp = OTPVerification.query.filter_by(
                user_identifier=identifier, 
                is_used=False
            ).order_by(OTPVerification.created_at.desc()).first()
            
            if otp and otp.expires_at > now and str(otp.otp_code).strip() == str(input_code).strip():
                otp.is_used = True 
                db.session.commit()
                return True
        except Exception:
            db.session.rollback()
            
        return False
