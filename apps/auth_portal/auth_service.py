# coding: utf-8
# 📂 apps/auth_portal/auth_service.py - النسخة المصححة نهائياً للمسار

import os
import requests
import json

class AdminAuthService:
    @staticmethod
    def initiate_login(phone, otp_code):
        # 1. التحقق من وجود المفاتيح قبل البدء
        api_key = os.environ.get('HYPERSEND_API_KEY')
        instance_id = os.environ.get('HYPERSEND_INSTANCE_ID')
        
        if not api_key or not instance_id:
            print("CRITICAL: المتغيرات البيئية (HYPERSEND_API_KEY أو HYPERSEND_INSTANCE_ID) مفقودة!")
            return False
        
        # 2. تنظيف الرقم
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        if not clean_phone.startswith('967'):
            clean_phone = '967' + clean_phone.lstrip('0')
        
        # المسار المصحح: إضافة 'messages' هو التعديل الجوهري بناءً على رسالة الخطأ
        url = "https://app.hypersender.com/api/v1/messages/send"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "instance_id": instance_id,
            "number": clean_phone,
            "type": "text",
            "message": f"رمز الدخول لمحجوب أونلاين هو: {otp_code}"
        }

        try:
            # 3. طباعة التشخيص
            print(f"DEBUG: محاولة الاتصال بـ {url}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            # 4. تحليل النتيجة
            print(f"DEBUG: Status Code: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print("✅ نجاح: تم إرسال الرمز.")
                return True
            else:
                try:
                    error_data = response.json()
                    print(f"CRITICAL: HyperSender JSON Error: {error_data}")
                except:
                    print(f"CRITICAL: HyperSender Raw Error: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"CRITICAL: Connection/Network Error: {str(e)}")
            return False
