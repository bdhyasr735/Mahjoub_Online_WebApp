# coding: utf-8
# 📂 apps/models/otp_db.py - نظام إدارة الرموز والتحقق السيادي (OTP Engine - AES256)

import random
from apps.extensions import db
from apps.utils.security import AESCipher
from datetime import datetime, timedelta

class OTPVerification(db.Model):
    __tablename__ = 'otp_verifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(150), index=True, nullable=False) 
    
    # تخزين الرمز مشفراً بمعيار AES-256
    _otp_code_enc = db.Column('otp_code', db.String(255), nullable=False)
    
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    def generate_otp(email, expires_in_minutes=5):
        """توليد رمز جديد صالح لـ 5 دقائق وإلغاء أي رموز سابقة لنفس البريد"""
        # إبطال الرموز السابقة لضمان سيادة الرمز الأحدث
        OTPVerification.query.filter_by(user_email=email, is_used=False).update({"is_used": True})
        
        raw_code = str(random.randint(100000, 999999))
        
        new_otp = OTPVerification(
            user_email=email,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes),
            otp_code=raw_code # استخدام الـ setter المشفر
        )
        db.session.add(new_otp)
        db.session.commit()
        
        return raw_code

    @staticmethod
    def verify_otp(email, input_code):
        """التحقق من صحة الرمز واستهلاكه فوراً لمنع هجمات إعادة الاستخدام"""
        now = datetime.utcnow()
        # البحث عن الرمز النشط الأحدث
        otp = OTPVerification.query.filter_by(
            user_email=email, 
            is_used=False
        ).order_by(OTPVerification.created_at.desc()).first()
        
        if otp and otp.expires_at > now and otp.otp_code == str(input_code):
            otp.is_used = True # استهلاك الرمز
            db.session.commit()
            return True
        return False
