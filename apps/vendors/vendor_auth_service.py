# 📂 apps/vendors/vendor_auth_service.py

from functools import wraps
from flask import session, redirect, url_for

def vendor_login_required(f):
    """
    حارس المسارات (Decorator): يقوم بالتأكد من أن المورد قد أتم الـ OTP
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'vendor_authenticated' not in session:
            return redirect(url_for('vendors.login_page')) # توجيه لصفحة تسجيل الدخول
        return f(*args, **kwargs)
    return decorated_function

def verify_otp_logic(user_input, actual_otp):
    """
    المنطق الخاص بمقارنة الرمز (بدون تعقيد)
    """
    return user_input == actual_otp
