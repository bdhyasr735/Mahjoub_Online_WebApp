# coding: utf-8
# 📂 apps/auth_portal/auth_service.py - محرك إرسال الرموز (إصدار V1 التوافقي النهائي)

import os
import requests
import time

class AdminAuthService:
    @staticmethod
    def initiate_login(phone, otp_code, retries=3):
        """
        إرسال الرمز عبر خدمة الرسائل المباشرة باستخدام API V1 الموحد 
        لضمان التوافق مع كافة خطط HyperSender وتجاوز أخطاء 404.
        """
        # سحب البيانات من متغيرات البيئة في Render
        api_key = os.environ.get('HYPERSEND_API_KEY')
        instance_id = os.environ.get('HYPERSEND_INSTANCE_ID')
        
        # تنظيف الرقم وتنسيقه
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        if not clean_phone.startswith('967'):
            clean_phone = '967' + clean_phone.lstrip('0')
        
        # الرابط الموحد للخطط (V1) - هذا المسار هو الأكثر استقراراً وقبولاً لدى الخوادم
        url = f"https://app.hypersender.com/api/v1/instance/{instance_id}/message"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # هيكل الرسالة القياسي (نظام V1)
        payload = {
            "number": f"{clean_phone}@c.us",
            "type": "text",
            "message": f"رمز الدخول لمحجوب أونلاين هو: {otp_code}"
        }

        print(f"DEBUG: محاولة إرسال رسالة إلى {clean_phone} عبر Instance: {instance_id}")

        for attempt in range(retries):
            try:
                # إرسال الطلب مع مهلة زمنية 15 ثانية لتجنب تعليق السيرفر
                response = requests.post(url, json=payload, headers=headers, timeout=15)
                
                # التحقق من نجاح العملية (كود 200)
                if response.status_code == 200:
                    print(f"✅ تم إرسال الرمز بنجاح إلى {clean_phone}")
                    return True
                else:
                    # تسجيل الخطأ في الـ Logs لاكتشاف سبب الـ 404 أو غيره من الأخطاء
                    print(f"DEBUG: فشل الإرسال (محاولة {attempt+1}) - كود {response.status_code}: {response.text}")
            
            except Exception as e:
                # تسجيل أي استثناء يحدث أثناء الاتصال
                print(f"🚨 [Admin Error]: {str(e)}")
            
            # انتظار قصير قبل إعادة المحاولة
            time.sleep(2)

        return False
