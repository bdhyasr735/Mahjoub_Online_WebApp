# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/whatsapp_api.py

import requests
import logging
import re
from flask import current_app

logger = logging.getLogger(__name__)

def clean_phone_number(phone):
    """تنظيف وتنسيق رقم الهاتف لإزالة الرموز الزائدة"""
    if not phone:
        return ""
    # إزالة أي رموز غير الأرقام ما عدا علامة الزائد إن وجدت
    cleaned = re.sub(r'[^\d+]', '', str(phone))
    return cleaned

class WhatsAppAPI:
    def __init__(self, token=None, phone_number_id=None, api_version=None):
        self.token = token or current_app.config.get('WHATSAPP_TOKEN', '') or current_app.config.get('WHATSAPP_ACCESS_TOKEN', '')
        self.phone_number_id = phone_number_id or current_app.config.get('WHATSAPP_PHONE_NUMBER_ID', '')
        self.api_version = api_version or current_app.config.get('WHATSAPP_API_VERSION', 'v17.0')
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"

    def send_text_message(self, recipient_phone, message_body):
        if not self.token or not self.phone_number_id:
            logger.error("⚠️ [WhatsApp API]: بيانات المصادقة أو معرف رقم الهاتف مفقودة.")
            return 400, {"error": "WhatsApp credentials not configured"}

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone_number(recipient_phone),
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message_body
            }
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=15)
            try:
                res_data = response.json()
            except:
                res_data = {"raw_text": response.text}
            return response.status_code, res_data
        except requests.exceptions.RequestException as e:
            logger.error(f"⚠️ [WhatsApp API Exception]: {e}")
            return 500, {"error": str(e)}

    def send_template_message(self, recipient, template_name, language_code="ar", components=None):
        if not self.token or not self.phone_number_id:
            return 400, {"error": "WhatsApp credentials not configured"}

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone_number(recipient),
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }

        if components:
            payload["template"]["components"] = components

        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=15)
            try:
                res_data = response.json()
            except:
                res_data = {"raw_text": response.text}
            return response.status_code, res_data
        except requests.exceptions.RequestException as e:
            return 500, {"error": str(e)}

    def send_media_message(self, recipient, media_url, media_type="image", caption=None):
        if not self.token or not self.phone_number_id:
            return 400, {"error": "WhatsApp credentials not configured"}

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        media_obj = {"link": media_url}
        if caption and media_type in ["image", "document", "video"]:
            media_obj["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone_number(recipient),
            "type": media_type,
            media_type: media_obj
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=20)
            try:
                res_data = response.json()
            except:
                res_data = {"raw_text": response.text}
            return response.status_code, res_data
        except requests.exceptions.RequestException as e:
            return 500, {"error": str(e)}

    def test_connection(self):
        if not self.token or not self.phone_number_id:
            return False
        test_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False


# الدوال العامة المساعدة التي تستوردها بقية ملفات المشروع
def send_text_message(recipient_phone, message_body):
    client = WhatsAppAPI()
    return client.send_text_message(recipient_phone, message_body)

def send_template_message(recipient, template_name, language_code="ar", components=None):
    client = WhatsAppAPI()
    return client.send_template_message(recipient, template_name, language_code, components)

def send_media_message(recipient, media_url, media_type="image", caption=None):
    client = WhatsAppAPI()
    return client.send_media_message(recipient, media_url, media_type, caption)

def send_meta_whatsapp_message(recipient_phone, message_body):
    """دالة إضافية متوافقة مع الاستدعاءات القديمة"""
    client = WhatsAppAPI()
    status, response = client.send_text_message(recipient_phone, message_body)
    if 200 <= status < 300:
        return response if isinstance(response, dict) else {"messages": [{"id": "sent_success"}]}
    else:
        return {}