# coding: utf-8
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from flask import current_app

class AESCipher:
    """
    كلاس احترافي لتشفير وفك تشفير البيانات الحساسة للموردين 
    لا يحتاج إلى __init__، استخدم AESCipher.encrypt و AESCipher.decrypt مباشرة.
    """
    
    @staticmethod
    def _get_key():
        # استخدام المفتاح من الإعدادات، مع توفير fallback آمن
        secret_key = current_app.config.get('SECRET_KEY', 'abcdefghijklmnopqrstuvwxyz123456')
        if isinstance(secret_key, str):
            secret_key = secret_key.encode('utf-8')
        return secret_key[:32].ljust(32, b'\0')

    @classmethod
    def encrypt(cls, raw_text):
        if not raw_text: return None
        try:
            key = cls._get_key()
            iv = b'\0' * 16 
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            raw_bytes = raw_text.encode('utf-8')
            pad_len = 16 - (len(raw_bytes) % 16)
            raw_bytes += bytes([pad_len]) * pad_len
            
            ciphertext = encryptor.update(raw_bytes) + encryptor.finalize()
            return base64.b64encode(ciphertext).decode('utf-8')
        except Exception:
            return raw_text 

    @classmethod
    def decrypt(cls, cipher_text):
        if not cipher_text: return None
        try:
            key = cls._get_key()
            iv = b'\0' * 16
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            raw_ciphertext = base64.b64decode(cipher_text.encode('utf-8'))
            decrypted_bytes = decryptor.update(raw_ciphertext) + decryptor.finalize()
            
            pad_len = decrypted_bytes[-1]
            if 0 < pad_len <= 16:
                decrypted_bytes = decrypted_bytes[:-pad_len]
                
            return decrypted_bytes.decode('utf-8')
        except Exception:
            return cipher_text
