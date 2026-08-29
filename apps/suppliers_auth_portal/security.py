# apps/suppliers_auth_portal/security.py
import re
from functools import wraps
from flask import request, jsonify, session, abort
from datetime import datetime, timedelta

# نظام الحні وتتبع المحاولات الفاشلة مؤقتاً في الذاكرة (أو يمكن ربطه بـ Redis/DB)
FAILED_ATTEMPTS_STORE = {}

def validate_phone_number(phone):
    """التحقق من صحة تنسيق رقم الجوال اليمني أو الدولي"""
    if not phone:
        return False
    # يقبل الأرقام التي تبدأ بـ +967 أو 77, 73, 71, 70 أو 05 للسعودية
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
    if ip_address in FAILED_ATTEMPTS_STORE:
        attempts, lockout_until = FAILED_ATTEMPTS_STORE[ip_address]
        if lockout_until and now < lockout_until:
            remaining = int((lockout_until - now).total_seconds())
            return False, remaining
        elif lockout_until and now >= lockout_until:
            # انتهاء فترة الحظر
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
