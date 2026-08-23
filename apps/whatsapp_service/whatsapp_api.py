# coding: utf-8
# 📂 apps/whatsapp_service/whatsapp_api.py

"""
WhatsApp Cloud API Integration Module for Mahjoub Online
Handles sending text messages, templates, and media messages via Meta WhatsApp API
"""

import os
import requests
from datetime import datetime
from flask import current_app, has_app_context

BASE_URL = "https://graph.facebook.com"


# =========================================================
# دوال مساعدة لتهيئة البيانات وتفادي الأخطاء
# =========================================================

def clean_phone_number(phone: str) -> str:
    """
    تنظيف وتنسيق رقم الهاتف بالصيغة الدولية المعتمدة لدى Meta (بدون + أو 00)
    """
    if not phone:
        return ""
    cleaned = ''.join(filter(str.isdigit, str(phone)))
    if cleaned.startswith('00'):
        cleaned = cleaned[2:]
    elif cleaned.startswith('0') and len(cleaned) == 10:  # أرقام اليمن المحلية (07XXXXXXXX)
        cleaned = '967' + cleaned[1:]
    return cleaned


def get_config_val(key: str, default: str = "") -> str:
    """
    جلب قيم التكوين ديناميكياً من Flask current_app أو من متغيرات البيئة
    """
    if has_app_context() and key in current_app.config:
        val = current_app.config.get(key)
        if val:
            return str(val)
    return str(os.getenv(key, default))


def get_db():
    """
    الحصول على جلسة قاعدة البيانات بأمان تام وبدون استيراد دائري
    """
    from apps.extensions import db
    return db


def _log_message_to_db(recipient: str, content: str, status: str, wamid: str = None, msg_type: str = "text"):
    """
    دالة مساعدة لتوحيد تسجيل الرسائل المخرجة وتحديث جهة الاتصال
    """
    try:
        db = get_db()
        from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppCustomerContact

        phone_id = get_config_val("WHATSAPP_PHONE_NUMBER_ID")

        # 1. إنشاء سجل الرسالة
        log_entry = WhatsAppMessageLog(
            wamid=wamid,
            direction='outbound',
            sender_number=str(phone_id),
            recipient_number=str(recipient),
            content=content,
            status=status
        )
        if hasattr(log_entry, 'message_type'):
            log_entry.message_type = msg_type

        db.session.add(log_entry)

        # 2. تحديث آخر محادثة في جهة الاتصال
        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=str(recipient)).first()
        if contact:
            contact.last_message = content
            contact.last_timestamp = datetime.utcnow()

        db.session.commit()
    except Exception as e:
        try:
            get_db().session.rollback()
        except Exception:
            pass
        print(f"⚠️ [WhatsApp Log Error]: فشل حفظ السجل في قاعدة البيانات: {e}")


# =========================================================
# الدالة العامة لإرسال رسائل النص (Core API Function)
# =========================================================

def send_text_message(recipient: str, message: str) -> tuple[bool, dict]:
    """
    إرسال رسالة نصية إلى رقم معين عبر واتساب.
    """
    formatted_recipient = clean_phone_number(recipient)
    phone_id = get_config_val("WHATSAPP_PHONE_NUMBER_ID")
    token = get_config_val("WHATSAPP_ACCESS_TOKEN")
    ver = get_config_val("WHATSAPP_API_VERSION", get_config_val("VERSION", "v20.0"))

    if not phone_id or not token:
        return False, {"error": "بيانات الاعتماد المخصصة للواتساب غير معرفة (Phone ID / Token)"}

    url = f"{BASE_URL}/{ver}/{phone_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": formatted_recipient,
        "type": "text",
        "text": {"preview_url": False, "body": message}
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        res_data = response.json()

        wamid = None
        if response.status_code in [200, 201]:
            wamid = res_data.get('messages', [{}])[0].get('id')
            _log_message_to_db(formatted_recipient, message, 'sent', wamid, msg_type='text')
            return True, res_data
        else:
            _log_message_to_db(formatted_recipient, message, 'failed', None, msg_type='text')
            return False, res_data

    except Exception as e:
        _log_message_to_db(formatted_recipient, message, 'failed', None, msg_type='text')
        return False, {"error": str(e)}


# =========================================================
# الدالة العامة لإرسال القوالب (Templates / Broadcast)
# =========================================================

def send_template_message(recipient: str, template_name: str, language_code: str = "ar", components: list = None) -> tuple[bool, dict]:
    """
    إرسال رسالة قالب معتمد من ميتا.
    """
    formatted_recipient = clean_phone_number(recipient)
    phone_id = get_config_val("WHATSAPP_PHONE_NUMBER_ID")
    token = get_config_val("WHATSAPP_ACCESS_TOKEN")
    ver = get_config_val("WHATSAPP_API_VERSION", get_config_val("VERSION", "v20.0"))

    if not phone_id or not token:
        return False, {"error": "بيانات الاعتماد المخصصة للواتساب غير معرفة"}

    url = f"{BASE_URL}/{ver}/{phone_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": formatted_recipient,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
            "components": components or []
        }
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        res_data = response.json()

        wamid = None
        log_content = f"[قالب: {template_name}]"
        
        if response.status_code in [200, 201]:
            wamid = res_data.get('messages', [{}])[0].get('id')
            _log_message_to_db(formatted_recipient, log_content, 'sent', wamid, msg_type='template')
            return True, res_data
        else:
            _log_message_to_db(formatted_recipient, log_content, 'failed', None, msg_type='template')
            return False, res_data

    except Exception as e:
        _log_message_to_db(formatted_recipient, f"[قالب: {template_name}]", 'failed', None, msg_type='template')
        return False, {"error": str(e)}


# =========================================================
# دالة إرسال الصور والوسائط
# =========================================================

def send_media_message(recipient: str, media_url: str, media_type: str = "image", caption: str = None) -> tuple[bool, dict]:
    """
    إرسال صورة أو فيديو أو مستند عبر واتساب.
    """
    formatted_recipient = clean_phone_number(recipient)
    phone_id = get_config_val("WHATSAPP_PHONE_NUMBER_ID")
    token = get_config_val("WHATSAPP_ACCESS_TOKEN")
    ver = get_config_val("WHATSAPP_API_VERSION", get_config_val("VERSION", "v20.0"))

    if not phone_id or not token:
        return False, {"error": "بيانات الاعتماد المخصصة للواتساب غير معرفة"}

    url = f"{BASE_URL}/{ver}/{phone_id}/messages"
    media_object = {"link": media_url}
    if caption:
        media_object["caption"] = caption

    payload = {
        "messaging_product": "whatsapp",
        "to": formatted_recipient,
        "type": media_type,
        media_type: media_object
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        res_data = response.json()

        wamid = None
        log_content = f"[{media_type}: {media_url}]" + (f" - {caption}" if caption else "")

        if response.status_code in [200, 201]:
            wamid = res_data.get('messages', [{}])[0].get('id')
            _log_message_to_db(formatted_recipient, log_content, 'sent', wamid, msg_type=media_type)
            return True, res_data
        else:
            _log_message_to_db(formatted_recipient, log_content, 'failed', None, msg_type=media_type)
            return False, res_data

    except Exception as e:
        log_content = f"[{media_type}: {media_url}]"
        _log_message_to_db(formatted_recipient, log_content, 'failed', None, msg_type=media_type)
        return False, {"error": str(e)}


# =========================================================
# دالة التحقق من صحة الرقم
# =========================================================

def verify_phone_number(phone_number: str) -> dict:
    """
    فحص الأرقام وتنظيفها للتحقق من جاهزيتها للإرسال
    """
    cleaned = clean_phone_number(phone_number)
    if len(cleaned) >= 9:
        return {"valid": True, "formatted": cleaned, "message": "رقم صالح للإرسال"}
    return {"valid": False, "formatted": cleaned, "message": "رقم غير صحيح أو ناقص"}
