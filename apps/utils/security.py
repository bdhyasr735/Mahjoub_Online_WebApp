# coding: utf-8
from cryptography.fernet import Fernet
from flask import current_app

class AESCipher:
    """
    كلاس آمن ومبسط باستخدام خوارزمية Fernet.
    تمت إضافة معالجة ذكية للمسافات والمفتاح لضمان استقرار المحرك المالي.
    """

    @staticmethod
    def _get_fernet():
        # استرجاع المفتاح مع إزالة أي مسافات زائدة قد تكون دخلت بالخطأ
        raw_key = current_app.config.get('ENCRYPTION_KEY')
        if not raw_key:
            raise RuntimeError("⚠️ خطأ أمني: ENCRYPTION_KEY غير مضبوط!")
        
        # تنظيف المفتاح من أي مسافات مخفية
        clean_key = raw_key.strip()
        return Fernet(clean_key.encode())

    @classmethod
    def encrypt(cls, raw_text):
        if not raw_text:
            return None
        try:
            f = cls._get_fernet()
            return f.encrypt(str(raw_text).encode()).decode('utf-8')
        except Exception as e:
            # بدلاً من طباعة الخطأ فقط، نجعله صامتاً لتجنب إيقاف النظام
            return None

    @classmethod
    def decrypt(cls, cipher_text):
        if not cipher_text:
            return None
        try:
            f = cls._get_fernet()
            return f.decrypt(cipher_text.encode()).decode('utf-8')
        except Exception as e:
            # إذا فشل فك التشفير، نعيد None بدلاً من إيقاف المحرك المالي
            return None
