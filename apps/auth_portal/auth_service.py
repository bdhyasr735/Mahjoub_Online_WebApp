# coding: utf-8
# 📂 apps/auth_portal/auth_service.py - النسخة التشخيصية المكثفة

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
            print("CRITICAL: المتغيرات البيئية (API_KEY أو INSTANCE_ID) مفقودة!")
            return False
        
        # 2. تنظيف الرقم
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        if not clean_phone.startswith('967'):
            clean_phone = '967' + clean_phone.lstrip('0')
        
        url = "https://app.hypersender.com/api/v1/send"
        
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
            # 3. طباعة التشخيص الكامل قبل الإرسال
            print(f"DEBUG: URL: {url}")
            print(f"DEBUG: Headers: {headers}") # ملاحظة: الـ Bearer سيظهر هنا
            print(f"DEBUG: Payload: {json.dumps(payload)}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            # 4. كشف عميق لنتائج الاستجابة
            print(f"DEBUG: Status Code: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print("✅ نجاح: تم إرسال الرمز.")
                return True
            else:
                # محاولة قراءة رد الخادم كـ JSON إذا أمكن، وإلا كـ نص
                try:
                    error_data = response.json()
                    print(f"CRITICAL: HyperSender JSON Error: {error_data}")
                except:
                    print(f"CRITICAL: HyperSender Raw Error: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"CRITICAL: Connection/Network Error: {str(e)}")
            return False
