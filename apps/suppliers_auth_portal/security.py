# coding: utf-8
# apps/suppliers_auth_portal/security.py

from werkzeug.security import generate_password_hash, check_password_hash

class PasswordHasher:
    """فئة مسؤولة عن تشفير والتحقق من كلمات المرور باستخدام Werkzeug"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """توليد هاش آمن لكلمة المرور"""
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password_hash: str, password: str) -> bool:
        """التحقق من تطابق كلمة المرور مع الهاش المخزن"""
        return check_password_hash(password_hash, password)


class CSRFProtector:
    """فئة إضافية لحماية نماذج المصادقة إذا لزم الأمر"""
    
    @staticmethod
    def validate_token(token: str) -> bool:
        # يمكن إضافة التحقق المخصص هنا أو الاعتماد على Flask-WTF
        return bool(token)
