import os
import requests
from flask import current_app

class VendorAuthService:
    @staticmethod
    def initiate_login(phone, otp_code):
        # قراءة الرابط من متغيرات البيئة في Render
        bridge_url = os.environ.get('BRIDGE_API_URL')
        api_key = os.environ.get('BRIDGE_API_KEY')
        
        payload = {
            "phone": phone,
            "message": f"رمز التحقق لمحجوب أونلاين هو: {otp_code}",
            "key": api_key  # تأمين الطلب
        }
        
        try:
            # الموقع يرسل أمر لجهازك (Bridge)
            response = requests.post(f"{bridge_url}/api/send", json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ [Bridge Error] لا يمكن الوصول للعقل المدبر: {e}")
            return False
