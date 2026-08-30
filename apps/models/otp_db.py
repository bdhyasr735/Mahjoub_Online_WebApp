# coding: utf-8
from apps.extensions import db
from datetime import datetime, timedelta
import hashlib
import secrets
import hmac
import os
import logging

logger = logging.getLogger(__name__)


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
        try:
            # إبطال أي رموز سابقة غير مستخدمة لنفس المعرف منعاً لتراكم رموز فعالة متعددة
            cls.query.filter(
                cls.identifier == identifier,
                cls.is_used == False,
                cls.is_blocked == False
            ).update({cls.is_used: True})

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
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ خطأ أثناء إنتاج رمز OTP: {str(e)}", exc_info=True)
            raise e

    def verify(self, otp_code: str) -> dict:
        now = datetime.utcnow()

        if self.is_used:
            return {'success': False, 'message': 'تم استخدام هذا الرمز مسبقاً'}

        if self.is_blocked and self.blocked_until:
            if now < self.blocked_until:
                remaining = int((self.blocked_until - now).total_seconds())
                return {'success': False, 'message': f'الحساب محظور مؤقتاً، يجدر الانتظار لمدة {remaining} ثانية'}
            else:
                # انتهاء فترة الحظر المؤقت تلقائياً
                self.is_blocked = False
                self.blocked_until = None
                self.attempts = 0
                db.session.commit()

        if now > self.expiry:
            return {'success': False, 'message': 'انتهت صلاحية رمز التحقق'}

        if self.attempts >= self.max_attempts:
            self.is_blocked = True
            self.blocked_until = now + timedelta(minutes=15)
            db.session.commit()
            return {'success': False, 'message': 'تم تجاوز الحد الأقصى للمحاولات، تم حظر الحساب مؤقتاً لمدة 15 دقيقة'}

        if not self._verify_otp(otp_code, self.otp_hash, self.otp_salt):
            self.attempts += 1
            if self.attempts >= self.max_attempts:
                self.is_blocked = True
                self.blocked_until = now + timedelta(minutes=15)
                message = 'تم تجاوز الحد الأقصى للمحاولات، تم حظر الحساب مؤقتاً لمدة 15 دقيقة'
            else:
                remaining_attempts = self.max_attempts - self.attempts
                message = f'رمز التحقق غير صحيح، تبقى لديك {remaining_attempts} محاولات'
            
            db.session.commit()
            return {'success': False, 'message': message}

        self.is_used = True
        db.session.commit()
        return {'success': True, 'message': 'تم التحقق بنجاح'}

    @classmethod
    def get_valid_otp(cls, otp_code: str, identifier: str = None):
        now = datetime.utcnow()
        query = cls.query.filter(
            cls.is_used == False,
            cls.is_blocked == False,
            cls.expiry > now
        )
        if identifier:
            query = query.filter(cls.identifier == identifier)
        
        # ترتيب تنازلي للأحدث لتفادي مطابقة رموز قديمة صالحة بالخطأ
        valid_otps = query.order_by(cls.created_at.desc()).all()
        for otp in valid_otps:
            # التحقق مما إذا كان الحظر المؤقت منتهياً في السجل الفردي
            if otp.blocked_until and now >= otp.blocked_until:
                otp.is_blocked = False
                otp.blocked_until = None
                otp.attempts = 0
                db.session.commit()

            if not otp.is_blocked and otp._verify_otp(otp_code, otp.otp_hash, otp.otp_salt):
                return otp
        return None

    @classmethod
    def verify_code_for_identifier(cls, identifier: str, otp_code: str) -> dict:
        """دالة مساعدة للبحث والتحقق مباشرة عبر المُعرف والرمز مع معالجة الحظر الشامل"""
        if not otp_code or not identifier:
            return {'success': False, 'message': 'بيانات التحقق غير مكتملة'}
            
        clean_code = str(otp_code).strip()
        
        # البحث عن أحدث سجل نشط أو محظور لنفس المعرف للتحقق من حالة الحظر الحالي
        latest_record = cls.query.filter_by(identifier=identifier).order_by(cls.created_at.desc()).first()
        now = datetime.utcnow()
        
        if latest_record and latest_record.is_blocked and latest_record.blocked_until:
            if now < latest_record.blocked_until:
                remaining = int((latest_record.blocked_until - now).total_seconds())
                return {'success': False, 'message': f'الحساب محظور مؤقتاً، يجدر الانتظار لمدة {remaining} ثانية'}
            else:
                latest_record.is_blocked = False
                latest_record.blocked_until = None
                latest_record.attempts = 0
                db.session.commit()

        otp_record = cls.get_valid_otp(clean_code, identifier)
        
        if not otp_record:
            # إذا لم يتم العثور على رمز صالح، نبحث في السجل الأحدث لتسجيل محاولة فاشلة وزيادة العدّاد إن وجد
            if latest_record and not latest_record.is_used and not latest_record.is_blocked:
                latest_record.attempts += 1
                if latest_record.attempts >= latest_record.max_attempts:
                    latest_record.is_blocked = True
                    latest_record.blocked_until = now + timedelta(minutes=15)
                    db.session.commit()
                    return {'success': False, 'message': 'تم تجاوز الحد الأقصى للمحاولات، تم حظر الحساب مؤقتاً لمدة 15 دقيقة'}
                db.session.commit()
                remaining_attempts = latest_record.max_attempts - latest_record.attempts
                return {'success': False, 'message': f'رمز التحقق غير صالح، تبقى لديك {remaining_attempts} محاولات'}

            return {'success': False, 'message': 'رمز التحقق غير صالح أو انتهت صلاحيته'}
            
        return otp_record.verify(clean_code)

    @classmethod
    def cleanup_expired_otps(cls):
        """حذف رموز التحقق المنتهية أو المستخدمة القديمة لتخفيف حجم الجدول"""
        try:
            threshold = datetime.utcnow() - timedelta(days=1)
            expired_records = cls.query.filter(
                (cls.expiry < threshold) | (cls.is_used == True)
            ).all()
            
            for record in expired_records:
                db.session.delete(record)
            db.session.commit()
            return len(expired_records)
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ خطأ أثناء تنظيف رموز OTP القديمة: {str(e)}", exc_info=True)
            return 0

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
