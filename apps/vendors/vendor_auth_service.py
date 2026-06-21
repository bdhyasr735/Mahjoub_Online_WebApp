# 📂 apps/vendors/vendor_auth_service.py
import requests
from apps.models.otp_db import OTPVerification

class VendorAuthService:
    API_KEY = "rb3tZFnHRcsN" 
    
    @staticmethod
    def send_whatsapp_otp(phone_number, otp_code):
        """إرسال الكود عبر واتساب مع تنظيف الرقم من الرموز"""
        # تنظيف الرقم: إزالة أي مسافات أو علامة "+"
        clean_phone = phone_number.replace("+", "").replace(" ", "")
        
        message = f"مرحباً، رمز التحقق لبوابة محجوب أونلاين هو: {otp_code}"
        encoded_message = requests.utils.quote(message)
        
        url = f"http://api.textmebot.com/send.php?recipient={clean_phone}&apikey={VendorAuthService.API_KEY}&text={encoded_message}"
        
        try:
            # إضافة timeout لتجنب تعليق السيرفر
            response = requests.get(url, timeout=10)
            # إضافة طباعة لحالة الاستجابة في الـ Logs لتسهيل التتبع
            print(f"TextMeBot Response: {response.status_code} - {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending WhatsApp: {e}")
            return False

    @staticmethod
    def initiate_login(phone):
        """بدء عملية الدخول: توليد كود وإرساله"""
        # توليد كود وتخزينه
        otp = OTPVerification.generate_otp(phone)
        
        if not otp:
            return False
            
        # إرسال الكود
        return VendorAuthService.send_whatsapp_otp(phone, otp)
