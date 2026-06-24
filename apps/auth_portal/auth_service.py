# coding: utf-8
# 📂 apps/auth_portal/auth_service.py - النسخة النهائية المطابقة للتكامل الديناميكي

import os
import requests

class AdminAuthService:
    @staticmethod
    def initiate_login(phone, otp_code):
        # 1. جلب الإعدادات من متغيرات البيئة (تأكد من إضافتها في Render Dashboard)
        api_key = os.environ.get('HYPERSEND_API_KEY')
        instance_id = os.environ.get('HYPERSEND_INSTANCE_ID')
        
        if not api_key or not instance_id:
            print("CRITICAL: Missing HYPERSEND_API_KEY or HYPERSEND_INSTANCE_ID")
            return False
        
        # 2. تنظيف الرقم (بدون أي مسافات)
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        if not clean_phone.startswith('967'):
            clean_phone = '967' + clean_phone.lstrip('0')
        
        # 3. التنسيق المطلوب لـ HyperSender
        chat_id = f"{clean_phone}@c.us"
        
        # 4. الرابط الصحيح (يجب تضمين instance_id في المسار وفقاً لتوثيق المنصة)
        url = f"https://app.hypersender.com/api/whatsapp/v1/instance/{instance_id}/send-text"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 5. الـ Payload
        payload = {
            "chatId": chat_id,
            "text": f"رمز الدخول لمحجوب أونلاين هو: {otp_code}"
        }

        try:
            print(f"DEBUG: محاولة الإرسال لـ {chat_id} عبر الإنستانس {instance_id}")
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code in [200, 201]:
                print("✅ نجاح: تم إرسال الرمز بنجاح.")
                return True
            else:
                # طباعة تفاصيل الخطأ القادم من المنصة
                print(f"CRITICAL: HyperSender Error {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"CRITICAL: Connection Error: {str(e)}")
            return False
