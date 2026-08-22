# coding: utf-8
# 📂 apps/whatsapp_service/whatsapp_api.py

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
VERSION = os.getenv("VERSION", "v20.0")
BASE_URL = "https://graph.facebook.com"
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mahjoub_secure_webhook_token")


def get_db():
    try:
        from app import db
        return db
    except Exception:
        from apps.extensions import db
        return db


# ==========================================
# الدالة العامة لإرسال رسائل النص (Core API Function)
# ==========================================
def send_text_message(recipient, message):
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
        
        wamid = None
        try:
            wamid = res_data.get('messages', [{}])[0].get('id')
        except Exception:
            pass
            
        status = 'sent' if response.status_code == 200 else 'failed'
        
        # حفظ السجل
        log_entry = WhatsAppMessageLog(
            wamid=wamid,
            direction='outbound', 
            sender_number=str(phone_id), 
            recipient_number=str(recipient), 
            content=message, 
            status=status
        )
        db.session.add(log_entry)

        # تحديث آخر رسالة وجهة الاتصال
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
