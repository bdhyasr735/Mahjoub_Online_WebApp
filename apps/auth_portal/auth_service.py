# coding: utf-8
# 📂 apps/auth_portal/auth_service.py - النسخة المصححة نهائياً

import os
import requests

class AdminAuthService:
    @staticmethod
    def initiate_login(phone, otp_code):
        """
        إرسال رمز التحقق عبر خدمة HyperSender.
        """
        # 1. سحب البيانات من متغيرات البيئة (Render Environment Variables)
        api_key = os.environ.get('HYPERSEND_API_KEY')
        instance_id = os.environ.get('HYPERSEND_INSTANCE_ID')
        
        # 2. تنظيف الرقم (تنسيق دولي)
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        if not clean_phone.startswith('967'):
            clean_phone = '967' + clean_phone.lstrip('0')
        
        # 3. الرابط المصحح لـ API V1
        url = f"https://app.hypersender.com/api/v1/instance/{instance_id}/message"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 4. الهيكل القياسي للرسالة
        payload = {
            "number": clean_phone,
            "type": "text",
            "message": f"رمز الدخول لمحجوب أونلاين هو: {otp_code}"
        }

        try:
            # طباعة معلومات التشخيص (سيظهر هذا في سجلات Render)
            print(f"DEBUG: الاتصال بـ {url}")
            print(f"DEBUG: Payload: {payload}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            # 5. تحليل النتيجة والتعامل مع حالات النجاح والخطأ
            if response.status_code in [200, 201]:
                print(f"✅ نجاح: تم إرسال الرمز لـ {clean_phone}")
                return True
            else:
                # تسجيل الخطأ بالتفصيل لتشخيصه
                print(f"CRITICAL: HyperSender Error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            # تسجيل أي استثناء يحدث أثناء الاتصال
            print(f"CRITICAL: Connection Error: {str(e)}")
            return False
