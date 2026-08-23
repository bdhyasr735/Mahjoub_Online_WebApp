# coding: utf-8
# 📂 apps/whatsapp_service/whatsapp_api.py

"""
WhatsApp Cloud API Integration Module for Mahjoub Online
Handles sending text messages, templates, and media messages via Meta WhatsApp API
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# =========================================================
# إعدادات الاتصال الأساسية (تُقرأ من متغيرات البيئة)
# =========================================================
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
VERSION = os.getenv("VERSION", "v20.0")
BASE_URL = "https://graph.facebook.com"
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mahjoub_secure_webhook_token")


# =========================================================
# دالة مساعدة للحصول على اتصال قاعدة البيانات (تجنب Circular Import)
# =========================================================
def get_db():
    """
    الحصول على جلسة قاعدة البيانات بأمان مع تجنب الـ Circular Import.
    """
    try:
        from app import db
        return db
    except Exception:
        from apps.extensions import db
        return db


# =========================================================
# الدالة العامة لإرسال رسائل النص (Core API Function)
# =========================================================
def send_text_message(recipient, message):
    """
    إرسال رسالة نصية إلى رقم معين عبر واتساب.
    
    Args:
        recipient (str): رقم الهاتف المستلم (بالصيغة الدولية، مثال: 966501234567)
        message (str): محتوى الرسالة النصية
    
    Returns:
        tuple: (bool, dict) -> (نجاح العملية, بيانات الاستجابة من ميتا)
    """
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", PHONE_NUMBER_ID)
    token = os.getenv("WHATSAPP_ACCESS_TOKEN", ACCESS_TOKEN)
    ver = os.getenv("VERSION", VERSION)

    url = f"{BASE_URL}/{ver}/{phone_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": message}
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        res_data = response.json()

        db = get_db()
        from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppCustomerContact

        # استخراج معرف الرسالة من ميتا (WAMID)
        wamid = None
        try:
            wamid = res_data.get('messages', [{}])[0].get('id')
        except Exception:
            pass

        status = 'sent' if response.status_code == 200 else 'failed'

        # حفظ سجل الرسالة في قاعدة البيانات
        log_entry = WhatsAppMessageLog(
            wamid=wamid,
            direction='outbound',
            sender_number=str(phone_id),
            recipient_number=str(recipient),
            content=message,
            status=status
        )
        db.session.add(log_entry)

        # تحديث آخر رسالة في جهة الاتصال
        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=str(recipient)).first()
        if contact:
            contact.last_message = message
            contact.last_timestamp = datetime.utcnow()

        db.session.commit()

        if response.status_code == 200:
            return True, res_data
        else:
            return False, response.text

    except Exception as e:
        try:
            db = get_db()
            db.session.rollback()
        except Exception:
            pass
        return False, str(e)


# =========================================================
# الدالة العامة لإرسال القوالب (Templates / Broadcast)
# =========================================================
def send_template_message(recipient, template_name, language_code="ar", components=None):
    """
    إرسال رسالة قالب معتمد من ميتا (للإرسال الجماعي والتسويق).
    
    Args:
        recipient (str): رقم الهاتف المستلم
        template_name (str): اسم القالب المسجل في لوحة ميتا
        language_code (str): رمز اللغة (افتراضي: ar)
        components (list): مكونات القالب (رؤوس، أزرار، إلخ)
    
    Returns:
        tuple: (bool, dict) -> (نجاح العملية, بيانات الاستجابة)
    """
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", PHONE_NUMBER_ID)
    token = os.getenv("WHATSAPP_ACCESS_TOKEN", ACCESS_TOKEN)
    ver = os.getenv("VERSION", VERSION)

    url = f"{BASE_URL}/{ver}/{phone_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
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

        db = get_db()
        from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppCustomerContact

        # استخراج معرف الرسالة من ميتا (WAMID)
        wamid = None
        try:
            wamid = res_data.get('messages', [{}])[0].get('id')
        except Exception:
            pass

        status = 'sent' if response.status_code == 200 else 'failed'

        # حفظ سجل الرسالة في قاعدة البيانات
        log_entry = WhatsAppMessageLog(
            wamid=wamid,
            direction='outbound',
            sender_number=str(phone_id),
            recipient_number=str(recipient),
            content=f"[Template: {template_name}]",
            status=status
        )
        db.session.add(log_entry)

        # تحديث آخر رسالة في جهة الاتصال
        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=str(recipient)).first()
        if contact:
            contact.last_message = f"[قالب: {template_name}]"
            contact.last_timestamp = datetime.utcnow()

        db.session.commit()

        if response.status_code == 200:
            return True, res_data
        else:
            return False, response.text

    except Exception as e:
        try:
            db = get_db()
            db.session.rollback()
        except Exception:
            pass
        return False, str(e)


# =========================================================
# دالة إرسال الصور والوسائط (قيد التطوير)
# =========================================================
def send_media_message(recipient, media_url, media_type="image", caption=None):
    """
    إرسال صورة أو فيديو أو مستند عبر واتساب.
    
    Args:
        recipient (str): رقم الهاتف المستلم
        media_url (str): رابط الوسائط (يجب أن يكون HTTPS)
        media_type (str): نوع الوسائط (image, video, document, audio)
        caption (str): نص تعليق اختياري
    
    Returns:
        tuple: (bool, dict) -> (نجاح العملية, بيانات الاستجابة)
    """
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", PHONE_NUMBER_ID)
    token = os.getenv("WHATSAPP_ACCESS_TOKEN", ACCESS_TOKEN)
    ver = os.getenv("VERSION", VERSION)

    url = f"{BASE_URL}/{ver}/{phone_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": media_type,
        media_type: {
            "link": media_url
        }
    }
    if caption:
        payload[media_type]["caption"] = caption

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        res_data = response.json()

        db = get_db()
        from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppCustomerContact

        wamid = None
        try:
            wamid = res_data.get('messages', [{}])[0].get('id')
        except Exception:
            pass

        status = 'sent' if response.status_code == 200 else 'failed'

        log_entry = WhatsAppMessageLog(
            wamid=wamid,
            direction='outbound',
            sender_number=str(phone_id),
            recipient_number=str(recipient),
            content=f"[{media_type}: {media_url}]" + (f" - {caption}" if caption else ""),
            message_type=media_type,
            status=status
        )
        db.session.add(log_entry)

        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=str(recipient)).first()
        if contact:
            contact.last_message = f"[{media_type}]" + (f" - {caption}" if caption else "")
            contact.last_timestamp = datetime.utcnow()

        db.session.commit()

        if response.status_code == 200:
            return True, res_data
        else:
            return False, response.text

    except Exception as e:
        try:
            db = get_db()
            db.session.rollback()
        except Exception:
            pass
        return False, str(e)


# =========================================================
# دالة التحقق من صحة الرقم (قيد التطوير)
# =========================================================
def verify_phone_number(phone_number):
    """
    التحقق من صحة رقم الهاتف عبر واتساب (يتطلب صلاحيات إضافية).
    
    Args:
        phone_number (str): رقم الهاتف المراد التحقق منه
    
    Returns:
        dict: معلومات حول صحة الرقم
    """
    # هذه الميزة تتطلب صلاحيات خاصة في ميتا
    # سيتم تنفيذها عند الحاجة
    return {"valid": True, "message": "رقم صالح (محاكاة)"}
