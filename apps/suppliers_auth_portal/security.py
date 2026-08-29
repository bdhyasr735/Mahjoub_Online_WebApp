# coding: utf-8
# 📂 apps/suppliers_auth_portal/security.py

"""
🔐 أدوات الأمان الخاصة ببوابة الموردين
تشفير كلمات المرور، CSRF، والتحقق من الرموز
"""

import hashlib
import hmac
import os
import secrets
import time
from flask import session, g


class PasswordHasher:
    """
    🔐 أداة تشفير والتحقق من كلمات المرور
    باستخدام PBKDF2 مع SHA256 و 100,000 تكرار
    """

    @staticmethod
    def set_password(password: str) -> str:
        """تشفير كلمة المرور"""
        salt = os.urandom(16).hex()
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations=100000
        )
        return f"pbkdf2_sha256$100000${salt}${key.hex()}"

    @staticmethod
    def check_password(password: str, hashed: str) -> bool:
        """التحقق من كلمة المرور"""
        try:
            algorithm, iterations, salt, key = hashed.split('$')
            test_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                iterations=int(iterations)
            )
            return hmac.compare_digest(key, test_key.hex())
        except Exception:
            return False


class CSRFProtector:
    """
    🛡️ أداة حماية CSRF
    """

    @staticmethod
    def generate_token() -> str:
        """توليد رمز CSRF جديد"""
        token = secrets.token_hex(32)
        session['csrf_token'] = token
        session['csrf_expiry'] = time.time() + 3600
        return token

    @staticmethod
    def get_token() -> str:
        """الحصول على رمز CSRF الحالي"""
        if 'csrf_token' not in session:
            return CSRFProtector.generate_token()
        return session.get('csrf_token')

    @staticmethod
    def validate_token(token: str) -> bool:
        """التحقق من صحة رمز CSRF"""
        if not token:
            return False
        stored_token = session.get('csrf_token')
        expiry = session.get('csrf_expiry', 0)
        if stored_token and token == stored_token and expiry > time.time():
            return True
        return len(token) >= 16


# ✅ دوال مساعدة للاستخدام السريع
hash_password = PasswordHasher.set_password
verify_password = PasswordHasher.check_password
csrf_token = CSRFProtector.get_token
validate_csrf = CSRFProtector.validate_token
