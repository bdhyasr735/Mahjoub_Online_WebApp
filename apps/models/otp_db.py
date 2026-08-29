# coding: utf-8
# 📂 apps/models/otp_db.py

"""
نموذج رموز التحقق (OTP) - للمصادقة الثنائية واستعادة كلمة المرور
نسخة محسّنة مع تشفير OTP وحماية إضافية
"""

from apps.extensions import db
from datetime import datetime, timedelta
import hashlib
import secrets
import hmac
import os


class OTP(db.Model):
    """نموذج رموز التحقق المؤقتة - نسخة آمنة ومشفرة"""
    __tablename__ = 'otp_codes'

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(255), nullable=False, index=True)
    
    # ✅ تخزين OTP مشفر (بدلاً من النص العادي)
    otp_hash = db.Column(db.String(128), nullable=False)  # SHA-256 hash
    otp_salt = db.Column(db.String(64), nullable=False)   # Salt للتشفير
    
    target_id = db.Column(db.Integer, nullable=False, index=True)
    target_type = db.Column(db.String(50), default='supplier')
    expiry = db.Column(db.DateTime, nullable=False, index=True)  # مفهرس للتسريع
    attempts = db.Column(db.Integer, default=0)
    max_attempts = db.Column(db.Integer, default=5)  # حد أقصى للمحاولات
    is_used = db.Column(db.Boolean, default=False, index=True)
    is_blocked = db.Column(db.Boolean, default=False)  # حظر بعد تجاوز المحاولات
    blocked_until = db.Column(db.DateTime, nullable=True)  # وقت انتهاء الحظر
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 جاهز
    user_agent = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ==================== دوال التشفير ====================
    
    @staticmethod
    def _hash_otp(otp_code: str, salt: str = None) -> tuple:
        """تشفير OTP باستخدام PBKDF2 مع Salt"""
        if salt is None:
            salt = os.urandom(16).hex()
        
        # استخدام PBKDF2 لتشفير قوي
        key = hashlib.pbkdf2_hmac(
            'sha256',
            otp_code.encode('utf-8'),
            salt.encode('utf-8'),
            iterations=100000  # 100,000 تكرار لمقاومة هجمات القوة العمياء
        )
        return key.hex(), salt

    @staticmethod
    def _verify_otp(otp_code: str, stored_hash: str, salt: str) -> bool:
        """التحقق من OTP باستخدام التشفير"""
        computed_hash, _ = OTP._hash_otp(otp_code, salt)
        return hmac.compare_digest(computed_hash, stored_hash)

    # ==================== إنشاء OTP ====================

    @classmethod
    def create_otp(
        cls,
        identifier: str,
        target_id: int,
        target_type: str = 'supplier',
        ip_address: str = None,
        user_agent: str = None,
        expiry_seconds: int = 300
    ) -> 'OTP':
        """
        إنشاء رمز تحقق جديد مع تشفير آمن
        
        Args:
            identifier: البريد الإلكتروني أو رقم الجوال
            target_id: معرف المستخدم
            target_type: نوع المستخدم (supplier/employee)
            ip_address: عنوان IP للمستخدم
            user_agent: متصفح المستخدم
            expiry_seconds: مدة صلاحية الرمز بالثواني (افتراضي 5 دقائق)
        
        Returns:
            OTP: كائن الرمز المُنشأ
        """
        # توليد OTP عشوائي
        otp_code = f"{secrets.randbelow(900000) + 100000}"
        
        # تشفير OTP
        otp_hash, otp_salt = cls._hash_otp(otp_code)
        
        # حساب وقت الانتهاء
        expiry = datetime.utcnow() + timedelta(seconds=expiry_seconds)
        
        # إنشاء السجل
        otp = cls(
            identifier=identifier,
            otp_hash=otp_hash,
            otp_salt=otp_salt,
            target_id=target_id,
            target_type=target_type,
            expiry=expiry,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow()
        )
        
        db.session.add(otp)
        db.session.commit()
        
        # إرجاع OTP مع الكائن (للإرسال عبر البريد/SMS)
        return otp, otp_code

    # ==================== التحقق من OTP ====================

    def verify(self, otp_code: str) -> dict:
        """
        التحقق من صحة الرمز مع جميع الضوابط الأمنية
        
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'data': dict
            }
        """
        # 1. التحقق من استخدام الرمز
        if self.is_used:
            return {
                'success': False,
                'message': 'تم استخدام هذا الرمز مسبقاً'
            }

        # 2. التحقق من الحظر
        if self.is_blocked:
            if self.blocked_until and datetime.utcnow() < self.blocked_until:
                remaining = int((self.blocked_until - datetime.utcnow()).total_seconds())
                return {
                    'success': False,
                    'message': f'الحساب محظور مؤقتاً. انتظر {remaining} ثانية'
                }
            else:
                # إلغاء الحظر إذا انتهت المدة
                self.is_blocked = False
                self.blocked_until = None
                db.session.commit()

        # 3. التحقق من الصلاحية
        if datetime.utcnow() > self.expiry:
            return {
                'success': False,
                'message': 'انتهت صلاحية رمز التحقق'
            }

        # 4. التحقق من عدد المحاولات
        if self.attempts >= self.max_attempts:
            self.is_blocked = True
            self.blocked_until = datetime.utcnow() + timedelta(minutes=15)
            db.session.commit()
            return {
                'success': False,
                'message': 'تم تجاوز عدد المحاولات المسموح بها. الحساب محظور لمدة 15 دقيقة'
            }

        # 5. التحقق من الرمز
        if not self._verify_otp(otp_code, self.otp_hash, self.otp_salt):
            self.attempts += 1
            db.session.commit()
            
            remaining_attempts = self.max_attempts - self.attempts
            return {
                'success': False,
                'message': f'رمز التحقق غير صحيح. تبقى {remaining_attempts} محاولات'
            }

        # ✅ نجاح التحقق
        self.is_used = True
        db.session.commit()
        
        return {
            'success': True,
            'message': 'تم التحقق بنجاح'
        }

    # ==================== دوال مساعدة ====================

    @classmethod
    def get_valid_otp(cls, otp_code: str, identifier: str = None) -> 'OTP':
        """
        البحث عن OTP صالح
        
        Args:
            otp_code: رمز التحقق (غير مشفر)
            identifier: البريد أو الجوال (اختياري)
        """
        query = cls.query.filter(
            cls.is_used == False,
            cls.is_blocked == False,
            cls.expiry > datetime.utcnow()
        )
        
        if identifier:
            query = query.filter(cls.identifier == identifier)
        
        # جلب جميع الرموز الصالحة
        valid_otps = query.all()
        
        # التحقق من الرمز مقابل التشفير
        for otp in valid_otps:
            if otp._verify_otp(otp_code, otp.otp_hash, otp.otp_salt):
                return otp
        
        return None

    @classmethod
    def cleanup_expired(cls):
        """حذف الرموز المنتهية وغير المستخدمة"""
        expired = cls.query.filter(
            cls.expiry < datetime.utcnow(),
            cls.is_used == False
        ).delete()
        db.session.commit()
        return expired

    # ==================== التمثيل ====================

    def to_dict(self):
        """تحويل إلى قاموس (بدون بيانات حساسة)"""
        return {
            'id': self.id,
            'identifier': self.identifier,
            'target_id': self.target_id,
            'target_type': self.target_type,
            'expiry': self.expiry.isoformat() if self.expiry else None,
            'is_used': self.is_used,
            'is_blocked': self.is_blocked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'remaining_attempts': self.max_attempts - self.attempts,
        }

    def __repr__(self):
        return f"<OTP {self.id} for {self.identifier}>"
