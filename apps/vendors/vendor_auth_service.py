import requests
import re
import os

class VendorAuthService:
    @staticmethod
    def initiate_login(phone, otp_code):
        clean_phone = re.sub(r'[^\d]', '', str(phone))
        if not clean_phone.startswith('+'):
            clean_phone = "+" + clean_phone
        
        # تأكد أن المفتاح صحيح وموجود في متغيرات البيئة
        api_key = os.environ.get('TEXTMEBOT_API_KEY', 'rb3tZFnHRcsN')
        
        base_url = "http://api.textmebot.com/send.php"
        params = {
            "recipient": clean_phone,
            "apikey": api_key,
            "text": f"رمز التحقق لمحجوب أونلاين هو: {otp_code}",
            "json": "yes"
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=15)
            # إضافة طباعة الاستجابة الحقيقية للـ Logs
            print(f"DEBUG [TextMeBot Response]: {response.status_code} - {response.text}")
            
            return response.status_code == 200
        except Exception as e:
            print(f"CRITICAL [TextMeBot Error]: {e}")
            return False
