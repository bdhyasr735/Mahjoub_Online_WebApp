import os
import requests
import time

class AdminAuthService:
    @staticmethod
    def initiate_login(phone, otp_code, retries=3):
        # سحب المتغيرات من بيئة Render
        api_key = os.environ.get('HYPERSEND_API_KEY')
        instance_id = os.environ.get('HYPERSEND_INSTANCE_ID')
        
        # تنسيق الرقم
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        if not clean_phone.startswith('967'):
            clean_phone = '967' + clean_phone.lstrip('0')
        
        # الرابط الموحد للـ API V1 (الأكثر استقراراً للخطة المجانية)
        url = f"https://app.hypersender.com/api/v1/instance/{instance_id}/message"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "number": f"{clean_phone}@c.us", 
            "type": "text",
            "message": f"رمز الدخول لمحجوب أونلاين هو: {otp_code}"
        }

        for attempt in range(retries):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    print(f"✅ تم إرسال الرمز بنجاح إلى {clean_phone}")
                    return True
                else:
                    # تسجيل الخطأ في الـ Logs لاكتشاف السبب (404، 401، الخ)
                    print(f"DEBUG: فشل الإرسال (كود {response.status_code}): {response.text}")
            
            except Exception as e:
                print(f"🚨 [Admin Error]: {str(e)}")
            
            time.sleep(2)
        return False
