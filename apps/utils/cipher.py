# coding: utf-8
# 📂 apps/utils/cipher.py

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class AESCipher:
    def __init__(self, key: str):
        # تحويل المفتاح النصي إلى مفتاح تشفير صالح بـ 32 بايت
        salt = b'mahjoub_salt_2026' # ملح ثابت لتوليد المفتاح
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        self.fernet = Fernet(derived_key)

    def encrypt(self, plain_text: str) -> str:
        """تشفير النص"""
        if not plain_text: return ""
        encrypted_data = self.fernet.encrypt(plain_text.encode())
        return encrypted_data.decode()

    def decrypt(self, encrypted_text: str) -> str:
        """فك تشفير النص"""
        if not encrypted_text: return ""
        decrypted_data = self.fernet.decrypt(encrypted_text.encode())
        return decrypted_data.decode()
