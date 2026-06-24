# coding: utf-8
# 📂 apps/suppliers_auth_portal/auth_service.py - التحديث لنظام HyperSender V2 (الموردين)

import os
import requests
import time

class VendorAuthService:
    @staticmethod
    def initiate_login(phone, otp_code, retries=3):
        # ملاحظة: API الجديد V2 يتولى توليد الرمز وإرساله، لذا الكود هنا يطلب الطلب فقط
        api_key = os.environ.get('HYPERSEND_API_KEY', '572|GiAmlkPjuWPLAYThjSTenfaSruio6azmJ0laq0p1b30dd5a')
        
        # تنظيف الرقم وتنسيقه للـ API الجديد
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        if not clean_phone.startswith('967'):
            clean_phone = '967' + clean_phone.lstrip('0')
        
        formatted_chat_id = f"{clean_phone}@c.us"

        url = "https://app.hypersender.com/api/otp/v2/request-code"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # هيكل البيانات المعتمد في توثيق HyperSender V2
        payload = {
            "chatId": formatted_chat_id,
            "length": 6,
            "useLetter": False,
            "useNumber": True,
            "allCapital": False,
            "name": "MahjoubOnline",
            "expires": 1800
        }

        for attempt in range(retries):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=20)
                
                if response.status_code == 200:
                    print(f"✅ [Vendor OTP Sent V2] تم إرسال رمز المورد بنجاح.")
                    return True
                else:
                    print(f"❌ [HyperSender V2 Error - Supplier] الحالة: {response.status_code} - الرد: {response.text}")
            
            except Exception as e:
                print(f"🚨 [Vendor V2 Connection Error] محاولة {attempt + 1}: {str(e)}")
            
            time.sleep(2)

        return False
