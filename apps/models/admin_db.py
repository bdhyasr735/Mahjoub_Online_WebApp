# coding: utf-8
import os
import hashlib
from apps.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# ✅ إضافة الاستيراد المفقود هنا
from apps.utils import AESCipher 

# تهيئة مشفر البيانات السيادي
encryption_key = os.getenv('ENCRYPTION_KEY')
if not encryption_key:
    # سيستخدم هذا في حال نسيان المتغير في Render (للتطوير فقط)
    encryption_key = '00000000000000000000000000000000'

# تحريك التعريف داخل الكلاس أو التأكد من استيراد AESCipher
cipher = AESCipher(encryption_key)

class AdminUser(db.Model, UserMixin):
    # ... باقي الكود كما هو ...
