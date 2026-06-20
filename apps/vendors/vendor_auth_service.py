# coding: utf-8
# 📂 apps/vendors/vendor_auth_service.py

import requests
from flask import session
from functools import wraps
from flask import redirect, url_for, flash
from apps.models.otp_db import OTPVerification
from config import Config # تأكد من استيراد إعداداتك

def trigger_otp_process(email, full_phone):
    """
    1. توليد رمز صالح لمدة 5 دقائق.
    2. إرسال الرمز عبر واتساب.
    """
    # توليد الرمز (صلاحية 5 دقائق هي القيمة الافتراضية في الموديل)
    otp = OTPVerification.generate_otp(email, expires_in_minutes=5)
    
    # إرسال عبر الواتساب (استدعاء API)
    return send_whatsapp_otp(full_phone, otp)

def send_whatsapp_otp(phone, otp_code):
    """الربط الفعلي مع WhatsApp Business API"""
    url = f"https://graph.facebook.com/v18.0/{Config.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {Config.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": "otp_verification_template", # تأكد من تطابق الاسم في منصة ميتا
            "language": {"code": "ar"},
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": otp_code}]
                }
            ]
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 200

def verify_vendor_otp(email, otp):
    """استدعاء الموديل للتحقق الصارم"""
    return OTPVerification.verify_otp(email, otp)

def vendor_login_required(f):
    """ديكوريتور لحماية لوحة التحكم"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('vendor_authenticated'):
            return redirect(url_for('vendors.login_page'))
        return f(*args, **kwargs)
    return decorated_function
