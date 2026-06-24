# coding: utf-8
# 📂 apps/auth_portal/auth_service.py - محرك إرسال الرموز (متوافق مع الخطة المجانية)

import os
import requests
import time

class AdminAuthService:
    @staticmethod
    def initiate_login(phone, otp_code, retries=3):
        """
        إرسال الرمز عبر خدمة الرسائل العادية (للخطة المجانية).
        """
        api_key = os.environ.get('HYPERSEND_API_KEY', '572|GiAmlkPjuWPLAYThjSTenfaSruio6azmJ0laq0p1b30dd5a')
        
        # تنظيف الرقم
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        if not clean_phone.startswith('967'):
            clean_phone = '967' + clean_phone.lstrip('0')
        
        chat_id = f"{clean_phone}@c.us"
        
        # استخدام رابط إرسال الرسائل العادي (Endpoint للخطط المجانية)
        # تأكد من إضافة الـ Instance ID الخاص بك إذا كان مطلوباً في لوحة التحكم
        url = "https://app.hypersender.com/api/v1/messages/send"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # صياغة الرسالة كرسالة نصية عادية
        payload = {
            "chatId": chat_id,
            "contentType": "string",
            "content": f"رمز الدخول الخاص بك لمحجوب أونلاين هو: {otp_code}"
        }

        print(f"DEBUG: محاولة إرسال رسالة عادية إلى {chat_id}")

        for attempt in range(retries):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    print("✅ [Admin OTP] تم إرسال الرمز بنجاح كرسالة نصية.")
                    return True
                else:
                    print(f"DEBUG: فشل الإرسال (كود {response.status_code}): {response.text}")
            
            except Exception as e:
                print(f"🚨 [Admin Error]: {str(e)}")
            
            time.sleep(2)

        return False
