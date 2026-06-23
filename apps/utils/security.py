# coding: utf-8
# 📂 apps/utils/security.py - محرك التشفير السيادي (المُحدث بالمفتاح الصحيح)

from cryptography.fernet import Fernet
from apps.config import Config # استيراد المفتاح من ملف الإعدادات

class AESCipher:
    """محرك التشفير المعتمد على المفتاح المركزي في Config"""
    
    @staticmethod
    def _get_fernet():
        # استخدام المفتاح الموجود في ملف Config.py
        key = Config.ENCRYPTION_KEY.encode()
        return Fernet(key)

    @staticmethod
    def encrypt(raw_data):
        if not raw_data: return None
        return AESCipher._get_fernet().encrypt(str(raw_data).encode()).decode()

    @staticmethod
    def decrypt(enc_data):
        if not enc_data: return None
        try:
            return AESCipher._get_fernet().decrypt(enc_data.encode()).decode()
        except Exception:
            # إذا فشل الفك، فهذا يعني أن البيانات مشفرة بمفتاح آخر 
            # أو تم تعديلها، سنعيد None لتوليد OTP جديد
            return None
