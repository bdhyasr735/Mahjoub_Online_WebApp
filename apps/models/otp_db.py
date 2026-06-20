# coding: utf-8
# 📂 apps/models/otp_db.py - نظام إدارة الرموز والتحقق السيادي (OTP Engine - AES256)

import random
from apps.extensions import db
from apps.utils.security import AESCipher
from datetime import datetime, timedelta

class OTPVerification(db.Model):
    __tablename__ = 'otp_verifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(150), index=True, nullable=False) # البريد المستهدف للتحقق بالخطوة الأولى
    
    # تخزين الرمز مشفراً بمعيار AES-256 الفوقي لحظر القراءة المباشرة من قاعدة البيانات
    _otp_code_enc = db.Column('otp_code', db.String(255), nullable=False)
    
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Property للتحكم في الرمز وتشفيره تلقائياً عبر معيار المنصة ---
    @property
    def otp_code(self):
        """فك تشفير الرمز للمطابقة الخلفية أثناء عملية الدخول"""
        try:
            return AESCipher.decrypt(self._otp_code_enc) if self._otp_code_enc else None
        except Exception:
            return None

    @otp_code.setter
    def otp_code(self, value):
        """تشفير الرمز المكون من 6 أرقام بـ AES-256 قبل الحفظ"""
        if value:
            self._otp_code_enc = AESCipher.encrypt(str(value))
        else:
            self._otp_code_enc = None

    # --- العمليات الذكية للتحقق والتوليد حياً ---
    @staticmethod
    def generate_otp(email, expires_in_minutes=5):
        """توليد رمز جديد وإلغاء الرموز السابقة لنفس البريد تلقائياً لحظر التكرار"""
        # إلغاء الرموز القديمة غير المستخدمة لنفس الحساب فوراً
        OTPVerification.query.filter_by(user_email=email, is_used=False).update({"is_used": True})
        
        # توليد رمز عشوائي آمن مكون من 6 أرقام
        raw_code = str(random.randint(100000, 999999))
        
        new_otp = OTPVerification(
            user_email=email,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        )
        new_otp.otp_code = raw_code  # هنا يتم استدعاء الـ setter والتشفير بـ AES256 آلياً
        db.session.add(new_otp)
        
        return raw_code

    @staticmethod
    def verify_otp(email, input_code):
        """التحقق من صحة الرمز وصلاحيته الزمنية حياً واستهلاكه فوراً للسيادة الأمنية"""
        now = datetime.utcnow()
        active_otps = OTPVerification.query.filter_by(user_email=email, is_used=False).all()
        
        for otp in active_otps:
            # الـ getter يقوم بفك التشفير تلقائياً خلف الكواليس للمطابقة الحية
            if otp.expires_at > now and otp.otp_code == str(input_code):
                otp.is_used = True  # استهلاك الرمز فوراً لمنع إعادة استخدامه وثغرات الإعادة
                db.session.commit()
                return True
        return False
