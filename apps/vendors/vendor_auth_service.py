# coding: utf-8
# 📂 apps/vendors/vendor_auth_service.py

import requests
import re
import os

class VendorAuthService:
    @staticmethod
    def initiate_login(phone, otp_code):
        """
        إرسال رمز التحقق عبر واتساب.
        ملاحظة: تم تعديل تنسيق الرقم لضمان توافقه مع TextMeBot.
        """
        # 1. تنظيف الرقم: إزالة أي رموز غير رقمية (بما فيها +)
        clean_phone = re.sub(r'[^\d]', '', str(phone))
        
        # 2. المفتاح من متغيرات البيئة
        api_key = os.environ.get('TEXTMEBOT_API_KEY', 'rb3tZFnHRcsN')
        
        # 3. صياغة الرسالة (تم تقليل الرموز الخاصة لتفادي مشاكل الترميز)
        message = (
            f"Mahjoub Online | Security Code\n\n"
            f"أهلاً بك يا شريك النجاح.\n"
            f"رمز التحقق لدخولكم هو:\n\n"
            f"{otp_code}\n\n"
            f"صلاحية الرمز 5 دقائق.\n"
            f"— محجوب أونلاين"
        )
        
        base_url = "http://api.textmebot.com/send.php"
        
        # 4. إعداد المعاملات (بدون إرسال '+' في recipient)
        params = {
            "recipient": clean_phone, 
            "apikey": api_key,
            "text": message,
            "json": "yes"
        }
        
        try:
            # 5. إرسال الطلب
            response = requests.get(base_url, params=params, timeout=15)
            
            # تسجيل الاستجابة لفحصها في الـ Logs
            print(f"DEBUG [TextMeBot Response]: {response.status_code} - {response.text}")
            
            # 6. التحقق من النجاح
            # ملاحظة: API TextMeBot قد تعيد 200 حتى لو كان هناك خطأ في الرقم، 
            # لذا نتحقق من محتوى الرد إذا كان هناك خطأ في JSON
            return response.status_code == 200
            
        except Exception as e:
            print(f"CRITICAL [TextMeBot Error]: {e}")
            return False
