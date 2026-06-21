# coding: utf-8
# 📂 apps/vendors/vendor_auth_service.py

import requests
import re
import os

class VendorAuthService:
    @staticmethod
    def initiate_login(phone, otp_code):
        """
        إرسال رمز التحقق عبر واتساب بأسلوب عالمي احترافي 
        يعكس قوة النظام الذكي للسيادة الرقمية.
        """
        # تنظيف الرقم والتأكد من وجود مفتاح الدولة
        clean_phone = re.sub(r'[^\d]', '', str(phone))
        if not clean_phone.startswith('+'):
            clean_phone = "+" + clean_phone
        
        # المفتاح من متغيرات البيئة أو القيمة الافتراضية
        api_key = os.environ.get('TEXTMEBOT_API_KEY', 'rb3tZFnHRcsN')
        
        # الرسالة المحدثة بالهوية الجديدة (AI-Security System)
        message = (
            f"Mahjoub Online | AI-Security System\n\n"
            f"أهلاً بك يا شريك النجاح.\n"
            f"قام نظامنا الذكي بتوليد رمز تحقق آمن لدخولكم:\n\n"
            f"🔐 *{otp_code}*\n\n"
            f"تنبيه أمني: هذا الرمز هو مفتاحك الخاص، لضمان أعلى مستويات السيادة الرقمية، يرجى عدم مشاركته مع أي طرف نهائياً.\n"
            f"*صلاحية الرمز 5 دقائق.*\n\n"
            f"— محجوب أونلاين | الإدارة الذكية للعمليات"
        )
        
        base_url = "http://api.textmebot.com/send.php"
        params = {
            "recipient": clean_phone,
            "apikey": api_key,
            "text": message,
            "json": "yes"
        }
        
        try:
            # إرسال الطلب مع مهلة زمنية 15 ثانية لضمان الاستجابة
            response = requests.get(base_url, params=params, timeout=15)
            
            # تسجيل الاستجابة في سجلات Render للتحقق من الحالة
            print(f"DEBUG [TextMeBot Response]: {response.status_code} - {response.text}")
            
            # التأكد من النجاح (Status 200)
            return response.status_code == 200
            
        except Exception as e:
            # تسجيل أي خطأ تقني في الاتصال
            print(f"CRITICAL [TextMeBot Error]: {e}")
            return False
