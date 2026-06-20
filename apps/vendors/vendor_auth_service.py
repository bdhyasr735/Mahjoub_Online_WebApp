# coding: utf-8
# 📂 apps/vendors/vendor_auth_service.py

import requests
from flask import session, redirect, url_for
from functools import wraps
from apps.models.otp_db import OTPVerification

def send_whatsapp_otp(phone, otp_code):
    """إرسال الرمز عبر خدمة TextMeBot"""
    
    # مفتاحك الشخصي من TextMeBot
    api_key = "rb3tZFnHRcsN" 
    
    # نص الرسالة
    message = f"رمز التحقق الخاص بك في محجوب أونلاين هو: {otp_code}"
    
    # الرابط الخاص بـ TextMeBot
    url = "http://api.textmebot.com/send.php"
    
    # المعاملات كما يتطلبها الـ API الخاص بهم
    params = {
        "recipient": phone, 
        "apikey": api_key,
        "text": message
    }
    
    try:
        # إرسال الطلب
        response = requests.get(url, params=params)
        
        # طباعة النتيجة في Logs للتأكد
        print(f"DEBUG: TextMeBot Response: {response.status_code}, {response.text}")
        
        # TextMeBot يعيد عادة 200 إذا تم قبول الطلب
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: Failed to send via TextMeBot: {e}")
        return False

def trigger_otp_process(email, full_phone):
    """
    1. توليد رمز صالح لمدة 5 دقائق.
    2. إرسال الرمز عبر واتساب.
    """
    # توليد الرمز
    otp = OTPVerification.generate_otp(email, expires_in_minutes=5)
    
    # إرسال عبر الواتساب باستخدام الخدمة الجديدة
    return send_whatsapp_otp(full_phone, otp)

def verify_vendor_otp(email, otp):
    """استدعاء الموديل للتحقق الصارم"""
    return OTPVerification.verify_otp(email, otp)

def vendor_login_required(f):
    """ديكوريتور لحماية لوحة التحكم"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('vendor_authenticated'):
            # التوجيه للرابط الرئيسي الخاص بـ Blueprint الموردين
            return redirect(url_for('vendors.index'))
        return f(*args, **kwargs)
    return decorated_function
