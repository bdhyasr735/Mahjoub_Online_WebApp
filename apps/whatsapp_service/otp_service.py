# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/otp_service.py
"""
سوق محجوب أونلاين - خدمة المصادقة وإرسال رموز التحقق OTP عبر واتساب
Dedicated OTP & Authentication Service for Meta Cloud API v26.0
"""

import os
import requests
from typing import Dict, Any, Optional

class WhatsAppOTPService:
    def __init__(self):
        self.api_version = os.getenv("WHATSAPP_API_VERSION", "v26.0")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
        
        # رابط Meta Graph API الرسمي للإرسال
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def send_otp_code(self, recipient_phone: str, otp_code: str, template_name: str = "mahjoob_auth_otp", language_code: str = "ar") -> Dict[str, Any]:
        """
        إرسال رمز التحقق (OTP) عبر قالب مصادقة معتمد من Meta.
        
        Parameters:
            recipient_phone (str): رقم الهاتف مع رمز الدولة (مثال: 967784439991)
            otp_code (str): رمز التحقق المكون من أرقام
            template_name (str): اسم قالب المصادقة المعتمد في Meta Business Manager
            language_code (str): لغة القالب (افتراضياً 'ar')
        """
        clean_phone = recipient_phone.replace("+", "").replace(" ", "").strip()

        # هيكل قالب المصادقة المعتمد من واتساب (Authentication Template)
        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": otp_code
                            }
                        ]
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": "0",
                        "parameters": [
                            {
                                "type": "text",
                                "text": otp_code
                            }
                        ]
                    }
                ]
            }
        }

        # وضع المحاكاة في حال عدم وجود توكن حقيقي
        if not self.access_token:
            print(f"🔐 [محاكاة OTP]: تم إنشاء الرمز {otp_code} وإرساله إلى الرقم {clean_phone}")
            return {
                "status": "simulated",
                "success": True,
                "otp_code": otp_code,
                "to": clean_phone
            }

        try:
            response = requests.post(self.base_url, headers=self._get_headers(), json=payload, timeout=10)
            res_data = response.json()
            
            if response.status_code == 200 and "messages" in res_data:
                return {"success": True, "data": res_data}
            else:
                return {"success": False, "error": res_data}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
