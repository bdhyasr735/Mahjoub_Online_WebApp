# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/security.py
"""
بوابة دخول التجار - وحدة الأمان والتحقق والرسائل (واتساب + بريد إلكتروني بديل)
"""

import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import session, request, flash, current_app

from apps.models.otp_db import OTP
from apps.whatsapp_service.service import WhatsAppService
from apps.models.supplier_db import Supplier

whatsapp_service = WhatsAppService()

# نظام الحماية وتتبع المحاولات الفاشلة (Rate Limiting)
FAILED_ATTEMPTS_STORE = {}

def validate_phone_number(phone):
    """التحقق من صحة تنسيق رقم الجوال اليمني أو الدولي"""
    if not phone:
        return False
    pattern = r'^(?:\+967|967)?(7[0137]\d{7}|0?[5]\d{8})$'
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    return bool(re.match(pattern, clean_phone))

def validate_email(email):
    """التحقق من صحة البريد الإلكتروني"""
    if not email:
        return False
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def check_rate_limit(ip_address, max_attempts=5, lockout_minutes=15):
    """حماية ضد هجمات القوة العمياء (Brute Force) وتجاوز المحاولات"""
    now = datetime.now()
    
    # تنظيف الذاكرة من المحاولات القديمة
    for key in list(FAILED_ATTEMPTS_STORE.keys()):
        attempts, lockout_until = FAILED_ATTEMPTS_STORE[key]
        if lockout_until and now > lockout_until:
            del FAILED_ATTEMPTS_STORE[key]
    
    if ip_address in FAILED_ATTEMPTS_STORE:
        attempts, lockout_until = FAILED_ATTEMPTS_STORE[ip_address]
        if lockout_until and now < lockout_until:
            remaining = int((lockout_until - now).total_seconds())
            return False, remaining
        elif lockout_until and now >= lockout_until:
            FAILED_ATTEMPTS_STORE[ip_address] = (0, None)
    
    return True, 0

def record_failed_attempt(ip_address, max_attempts=5, lockout_minutes=15):
    now = datetime.now()
    attempts, lockout_until = FAILED_ATTEMPTS_STORE.get(ip_address, (0, None))
    attempts += 1
    if attempts >= max_attempts:
        lockout_until = now + timedelta(minutes=lockout_minutes)
        FAILED_ATTEMPTS_STORE[ip_address] = (attempts, lockout_until)
        return lockout_minutes * 60
    else:
        FAILED_ATTEMPTS_STORE[ip_address] = (attempts, None)
        return 0

def clear_rate_limit(ip_address):
    if ip_address in FAILED_ATTEMPTS_STORE:
        del FAILED_ATTEMPTS_STORE[ip_address]


class SupplierAuthSecurity:
    
    @staticmethod
    def generate_and_send_otp(supplier: Supplier, channel: str = 'whatsapp') -> dict:
        """
        توليد رمز OTP وإرساله عبر الواتساب كخيار أساسي، وفي حال فشله أو طلبه يتم التبديل للإيميل كبديل.
        """
        try:
            # 1. تحديد المعرف الأساسي (رقم الجوال أو البريد)
            identifier = supplier.phone or supplier.email
            if not identifier:
                return {"success": False, "message": "لا يوجد رقم جوال أو بريد إلكتروني مسجل لهذا التاجر."}

            # 2. إنشاء رمز OTP جديد في قاعدة البيانات (صلاحية 5 دقائق = 300 ثانية)
            ip_addr = request.remote_addr if request else '127.0.0.1'
            ua_string = request.user_agent.string if request and request.user_agent else 'Web Portal'
            
            otp_record, otp_code = OTP.create_otp(
                identifier=identifier,
                target_id=supplier.id,
                target_type='supplier',
                ip_address=ip_addr,
                user_agent=ua_string,
                expiry_seconds=300
            )
            
            sent_successfully = False
            used_channel = channel

            # 3. محاولة الإرسال عبر الواتساب أولاً إذا طلب المستخدم وكان الجوال متاحاً
            if channel == 'whatsapp' and supplier.phone:
                welcome_name = supplier.store_name or supplier.owner_name or "عزيزنا التاجر"
                message_text = (
                    f"مرحباً بك {welcome_name} في سوق محجوب أونلاين 🛍️\n\n"
                    f"رمز التحقق الخاص بك لتسجيل الدخول هو: *{otp_code}*\n\n"
                    f"هذا الرمز صالح لمدة 5 دقائق. لا تشفه مع أحد."
                )
                
                wa_res = whatsapp_service.send_message(supplier.phone, message_text)
                if wa_res and wa_res.get('status') != 'failed' and 'error' not in wa_res:
                    sent_successfully = True
                else:
                    # فشل الواتساب، نتحول تلقائياً للبريد الإلكتروني كبديل آمن
                    used_channel = 'email'

            # 4. الإرسال عبر البريد الإلكتروني (إذا تم طلبه صراحة، أو كبديل تلقائي عند تعطل الواتساب)
            if (used_channel == 'email' or not sent_successfully) and supplier.email:
                email_sent = SupplierAuthSecurity._send_otp_email
