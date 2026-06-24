# coding: utf-8
# 📂 apps/auth_portal/auth_service.py - محرك إرسال الرموز السيادي (HyperSender V2)

import os
import requests
import time

class AdminAuthService:
    @staticmethod
    def initiate_login(phone, otp_code=None, retries=3):
        """
        إرسال طلب التحقق إلى HyperSender V2.
        ملاحظة: في V2 الخدمة هي من تولد الرمز، لذا otp_code هو وسيط إضافي 
        ويمكن تجاهله إذا كان النظام يعتمد على توليد الـ API للرمز.
        """
        api_key = os.environ.get('HYPERSEND_API_KEY', '572|GiAmlkPjuWPLAYThjSTenfaSruio6azmJ0laq0p1b30dd5a')
        
        # تنظيف الرقم والتأكد من صيغة 967xxxxxxxxx@c.us
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        if not clean_phone.startswith('967'):
            clean_phone = '967' + clean_phone.lstrip('0')
        
        chat_id = f"{clean_phone}@c.us"
        
        # الرابط المحدث لخدمة OTP في V2
        # تأكد من الرابط في لوحة تحكم HyperSender إذا كان مختلفاً
        url = "https://app.hypersender.com/api/otp/v2/request-code"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # الهيكل المطلوب لـ V2
        payload = {
            "chatId": chat_id,
            "length": 6,
            "useLetter": False,
            "useNumber": True,
            "allCapital": False,
            "name": "MahjoubOnline",
            "expires": 600 # 10 دقائق
        }

        print(f"DEBUG: محاولة إرسال OTP إلى {chat_id} عبر الرابط {url}")

        for attempt in range(retries):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=20)
                
                # طباعة الرد للتصحيح في حالة الفشل
                if response.status_code != 200:
                    print(f"DEBUG: فشل الإرسال (محاولة {attempt+1}) - كود الحالة: {response.status_code}")
                    print(f"DEBUG: محتوى الرد: {response.text}")
                
                if response.status_code == 200:
                    res_data = response.json()
                    # التحقق من نجاح العملية حسب هيكل V2
                    if res_data.get('status') == 'success':
                        print("✅ [Admin OTP] تم إرسال الرمز بنجاح عبر HyperSender V2.")
                        return True
            
            except Exception as e:
                print(f"🚨 [Admin Connection Error] محاولة {attempt + 1}: {str(e)}")
            
            time.sleep(2) # انتظار قبل المحاولة التالية

        return False
