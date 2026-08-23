# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/whatsapp_api.py

import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class WhatsAppAPI:
    def __init__(self, token=None, phone_number_id=None, api_version=None):
        """
        تهيئة عميل واتساب (WhatsApp Cloud API Client)
        يمكن جلب البيانات مباشرة من إعدادات التطبيق أو تمريرها كمعاملات.
        """
        self.token = token or current_app.config.get('WHATSAPP_TOKEN', '')
        self.phone_number_id = phone_number_id or current_app.config.get('WHATSAPP_PHONE_NUMBER_ID', '')
        self.api_version = api_version or current_app.config.get('WHATSAPP_API_VERSION', 'v17.0')
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"

    def send_text_message(self, recipient_phone, message_body):
        """
        إرسال رسالة نصية عبر WhatsApp Cloud API
        """
        if not self.token or not self.phone_number_id:
            logger.error("⚠️ [WhatsApp API]: بيانات المصادقة أو معرف رقم الهاتف مفقودة في الإعدادات.")
            return {"success": False, "error": "WhatsApp credentials not configured"}

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message_body
            }
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=15)
            response_data = response.json()

            if response.status_code == 200:
                logger.info(f"✅ [WhatsApp API]: تم إرسال الرسالة بنجاح إلى {recipient_phone}")
                return {"success": True, "data": response_data}
            else:
                logger.error(f"❌ [WhatsApp API Error]: فشل الإرسال - {response_data}")
                return {"success": False, "error": response_data}

        except requests.exceptions.RequestException as e:
            logger.error(f"⚠️ [WhatsApp API Exception]: خطأ في الاتصال بالخادم الخارجي: {e}")
            return {"success": False, "error": str(e)}

    def test_connection(self):
        """
        اختبار الاتصال وصلاحية الرمز (Token) مع منصة ميتا
        """
        if not self.token or not self.phone_number_id:
            return False

        test_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"⚠️ [WhatsApp Connection Test Error]: {e}")
            return False
