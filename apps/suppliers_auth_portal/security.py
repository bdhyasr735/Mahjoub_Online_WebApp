# coding: utf-8
# apps/suppliers_auth_portal/security.py

from werkzeug.security import generate_password_hash, check_password_hash
import secrets

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
    """فئة مسؤولة عن إدارة وحماية رموز CSRF"""
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """التحقق من توفر أو صحة الرمز"""
        return bool(token)

    @staticmethod
    def get_token() -> str:
        """توليد أو جلب رمز CSRF صالح للاستخدام في النماذج"""
        try:
            from flask_wtf.csrf import generate_csrf
            return generate_csrf()
        except Exception:
            # طريقة احتياطية في حال لم يتم تهيئة Flask-WTF بشكل مباشر
            return secrets.token_hex(32)
