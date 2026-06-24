# coding: utf-8
# 📂 apps/suppliers_auth_portal/auth_service.py - نظام إرسال رموز الموردين (HyperSender V2 المحصن)

import os
import requests
import time

class VendorAuthService:
    @staticmethod
    def initiate_login(phone, otp_code=None, retries=3):
        """
        إرسال طلب التحقق للموردين عبر API HyperSender V2.
        تم تعديل التوقيع ليتوافق مع نداءات الـ Dispatcher.
        """
        api_key = os.environ.get('HYPERSEND_API_KEY', '572|GiAmlkPjuWPLAYThjSTenfaSruio6azmJ0laq0p1b30dd5a')
        
        # تنظيف الرقم والتأكد من صيغة 967xxxxxxxxx@c.us
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        if not clean_phone.startswith('967'):
            clean_phone = '967' + clean_phone.lstrip('0')
        
        formatted_chat_id = f"{clean_phone}@c.us"

        # الرابط المعتمد لخدمة OTP في V2
        url = "https://app.hypersender.com/api/otp/v2/request-code"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # الهيكل المعتمد في V2
        payload = {
            "chatId": formatted_chat_id,
            "length": 6,
            "useLetter": False,
            "useNumber": True,
            "allCapital": False,
            "name": "MahjoubOnline",
            "expires": 1800
        }

        print(f"DEBUG: محاولة إرسال OTP للمورد {formatted_chat_id} إلى الرابط {url}")

        for attempt in range(retries):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=20)
                
                # تصحيح شامل في حال الفشل
                if response.status_code != 200:
                    print(f"❌ [HyperSender V2 Error] المحاولة {attempt+1} - الحالة: {response.status_code}")
                    print(f"❌ [Response Text] {response.text}")
                
                if response.status_code == 200:
                    res_data = response.json()
                    # التأكد من نجاح العملية من بيانات الـ JSON العائدة
                    if res_data.get('status') == 'success' or 'id' in res_data:
                        print(f"✅ [Vendor OTP Sent V2] تم إرسال الرمز بنجاح.")
                        return True
                    else:
                        print(f"⚠️ [HyperSender Warning] الرد لم يحتوي على status success: {res_data}")
            
            except Exception as e:
                print(f"🚨 [Vendor V2 Connection Error] محاولة {attempt + 1}: {str(e)}")
            
            time.sleep(2)

        return False
