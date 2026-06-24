# coding: utf-8
# 📂 apps/auth_portal/auth_service.py - نسخة محصنة ضد قفل الاتصال (HyperSend Retry-Enabled)

import os
import re
import requests
import time

class AdminAuthService:
    @staticmethod
    def initiate_login(phone, otp_code, retries=3):
        """إرسال رمز التحقق للإدارة العليا مع آلية إعادة محاولة ذكية."""
        api_key = os.environ.get('HYPERSEND_API_KEY', '1389|sudxqnVbeF8d1HHi1a8ogGRRzkb6LOJDXILMe0Pg70dbd12c')
        instance_id = os.environ.get('HYPERSEND_INSTANCE_ID', 'a219739b-b1b0-4c0b-858c-45d4d309e27f')

        # تنظيف الرقم
        clean_phone = re.sub(r'[^\d]', '', str(phone))
        if clean_phone.startswith('00967'):
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('7') and len(clean_phone) == 9:
            clean_phone = '967' + clean_phone
        elif clean_phone.startswith('07') and len(clean_phone) == 10:
            clean_phone = '967' + clean_phone[1:]

        message_body = (
            f"*Mahjoub Online | Admin Access*\n\n"
            f"رمز دخول الإدارة الخاص بك هو: *{otp_code}*\n\n"
            f"— محجوب أونلاين | النظام الأمني"
        )

        url = "https://hypersend.net/api/v1/messages/send-text"
        params = {"api_key": api_key}
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "instance_id": instance_id,
            "to": clean_phone,
            "message": message_body
        }

        # آلية إعادة المحاولة (Retry Logic)
        for attempt in range(retries):
            try:
                with requests.Session() as session:
                    response = session.post(url, params=params, json=payload, headers=headers, timeout=25)
                
                if response.status_code == 200:
                    res_data = response.json()
                    if res_data.get('status') == 'success' or res_data.get('success') is True:
                        print(f"✅ [Admin OTP Sent] تم التسليم في المحاولة {attempt + 1}")
                        return True
                
                print(f"⚠️ [Admin HyperSend Attempt {attempt + 1}] فشل، محاولة جديدة...")
            
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                print(f"🚨 [Admin Connection Error] محاولة {attempt + 1}: {str(e)}")
            
            except Exception as e:
                print(f"❌ [Admin Critical Error]: {str(e)}")
                break
            
            time.sleep(2) # انتظار قبل المحاولة التالية

        return False
