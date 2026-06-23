# coding: utf-8
import os
import requests
import re
import time

class AdminAuthService:
    @staticmethod
    def initiate_login(phone, otp_code):
        clean_phone = re.sub(r'[^\d]', '', str(phone))
        # استخدم مفتاح الموردين أو مفتاح إداري خاص إن وجد
        api_key = os.environ.get('TEXTMEBOT_API_KEY', 'rb3tZFnHRcsN') 
        
        message = f"Mahjoub Online | Admin Access\n\nرمز دخول الإدارة: {otp_code}\n— محجوب أونلاين"
        base_url = "http://api.textmebot.com/send.php"
        
        params = {"recipient": clean_phone, "apikey": api_key, "text": message, "json": "yes"}
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            
            # معالجة التأخير
            if response.status_code == 403 and "Delay needed" in str(response.text):
                time.sleep(10)
                response = requests.get(base_url, params=params, headers=headers, timeout=15)
            
            print(f"DEBUG [Admin OTP Response]: {response.status_code} - {response.text}")
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ [Admin Auth Error] {e}")
            return False
