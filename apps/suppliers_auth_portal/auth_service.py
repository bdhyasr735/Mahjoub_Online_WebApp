# coding: utf-8
# 📂 apps/suppliers_auth_portal/auth_service.py

import os
import re
import time
import requests

class VendorAuthService:
    @staticmethod
    def initiate_login(phone, otp_code):
        clean_phone = re.sub(r'[^\d]', '', str(phone))
        api_key = os.environ.get('TEXTMEBOT_API_KEY', 'rb3tZFnHRcsN')
        
        message = f"Mahjoub Online | Security Code\n\nرمز التحقق هو: {otp_code}\n— محجوب أونلاين"
        base_url = "http://api.textmebot.com/send.php"
        
        params = {"recipient": clean_phone, "apikey": api_key, "text": message, "json": "yes"}
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            # المحاولة الأولى
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            
            # التعامل مع التأخير المفروض من الخدمة
            if response.status_code == 403 and "Delay needed" in str(response.text):
                print("⚠️ [System] تم اكتشاف تأخير من TextMeBot، ننتظر 10 ثوانٍ...")
                time.sleep(10)
                response = requests.get(base_url, params=params, headers=headers, timeout=15)
            
            # التحقق من النجاح
            if response.status_code == 200:
                print(f"✅ [OTP Sent] تم إرسال الرمز بنجاح للرقم: {clean_phone}")
                return True
            else:
                print(f"❌ [OTP Delivery Failed] الحالة: {response.status_code} - الرد: {response.text}")
                return False
                
        except Exception as e:
            print(f"CRITICAL [TextMeBot Error]: {str(e)}")
            return False
