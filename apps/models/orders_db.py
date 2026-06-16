# coding: utf-8
# 📂 apps/models/orders_db.py
import os
from apps.extensions import db  # تصحيح مسار الاستيراد الموحد
from datetime import datetime
from cryptography.fernet import Fernet

# جلب مفتاح التشفير من متغيرات البيئة - تأكد من مطابقة الاسم الذي وضعته في Render
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') 
if not ENCRYPTION_KEY:
    # لتجنب كسر البناء، لا تقم بتوليد المفتاح عشوائياً هنا، بل يجب أن يأتي من البيئة
    raise ValueError("⚠️ خطأ سيادي: مفتاح التشفير ENCRYPTION_KEY غير موجود في متغيرات البيئة!")

cipher_suite = Fernet(ENCRYPTION_KEY.encode())

# ... (بقية كلاس ProcessedOrder يبقى كما هو)
