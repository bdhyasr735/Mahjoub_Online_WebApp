# coding: utf-8
# 📂 apps/auth_portal/auth_service.py - النسخة النهائية المعتمدة

import os
import requests
import json

class AdminAuthService:
    @staticmethod
    def initiate_login(phone, otp_code):
        # 1. جلب المفاتيح من متغيرات البيئة
        api_key = os.environ.get('HYPERSEND_API_KEY')
        instance_id = os.environ.get('HYPERSEND_INSTANCE_ID')
        
        if not api_key or not instance_id:
            print("CRITICAL: المفاتيح غير موجودة في متغيرات البيئة!")
            return False
        
        # 2. تنظيف الرقم (تحويل إلى صيغة 967...)
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        if not clean_phone.startswith('967'):
            clean_phone = '967' + clean_phone.lstrip('0')
            
        # 3. المسار الصحيح للمنصات التي تعتمد Instance ID في الرابط
        # نقوم بتمرير الـ instance_id في الرابط كما هو متعارف عليه في الـ API الخاص بـ HyperSender
        url = f"https://app.hypersender.com/api/v1/instance/{instance_id}/message"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # 4. الـ Payload لا يحتاج لـ instance_id لأنه موجود في الرابط
        payload = {
            "number": clean_phone,
            "type": "text",
            "message": f"رمز الدخول لمحجوب أونلاين هو: {otp_code}"
        }

        try:
            # 5. تنفيذ الطلب
            print(f"DEBUG: محاولة الاتصال بـ {url}")
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            # تحليل الرد
            print(f"DEBUG: Status Code: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print("✅ نجاح: تم إرسال الرمز بنجاح.")
                return True
            else:
                # طباعة تفاصيل الخطأ للتشخيص
                print(f"CRITICAL: HyperSender Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"CRITICAL: فشل الاتصال: {str(e)}")
            return False
