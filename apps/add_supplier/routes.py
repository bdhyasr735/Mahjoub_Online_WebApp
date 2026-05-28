from flask import Blueprint, render_template, request, jsonify
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import base64
import hashlib

add_supplier = Blueprint('add_supplier', __name__, template_folder='templates')

# كلمة السر الموحدة (يجب أن تكون متطابقة في JS و Python)
SECRET_PASSWORD = "YOUR_SUPER_SECRET_AES_KEY_256"

def decrypt_aes_cryptojs(encrypted_text, password):
    """فك تشفير رسالة مشفرة بواسطة CryptoJS (AES)"""
    # 1. فك تشفير Base64
    encrypted_data = base64.b64decode(encrypted_text)
    
    # 2. التحقق من تنسيق OpenSSL "Salted__"
    if encrypted_data[:8] != b'Salted__':
        raise ValueError("تنسيق التشفير غير مدعوم")
    
    salt = encrypted_data[8:16]
    ciphertext = encrypted_data[16:]
    
    # 3. اشتقاق المفتاح و IV باستخدام PBKDF2 (تنسيق OpenSSL الافتراضي)
    # 32 bytes key, 16 bytes iv
    key_iv = PBKDF2(password, salt, 48, count=10000, hmac_hash_module=hashlib.sha256)
    key = key_iv[:32]
    iv = key_iv[32:]
    
    # 4. فك التشفير
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(ciphertext)
    
    # 5. إزالة الحشوة (Padding)
    padding_len = decrypted_data[-1]
    return decrypted_data[:-padding_len].decode('utf-8')

@add_supplier.route('/add_supplier_submit', methods=['POST'])
def add_supplier_submit():
    # استلام البيانات المشفرة
    encrypted_payload = request.form.get('full_encrypted_data')
    
    if not encrypted_payload:
        return jsonify({"status": "error", "message": "لا توجد بيانات مشفرة"}), 400

    try:
        # فك التشفير
        decrypted_json = decrypt_aes_cryptojs(encrypted_payload, SECRET_PASSWORD)
        import json
        data = json.loads(decrypted_json)
        
        # معالجة البيانات (مثال)
        # new_supplier = Supplier(username=data['username'], ...)
        # db.session.add(new_supplier)
        
        return jsonify({"status": "success", "message": "تم فك التشفير والمعالجة بنجاح"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"خطأ في المعالجة: {str(e)}"}), 500
