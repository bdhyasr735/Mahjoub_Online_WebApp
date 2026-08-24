# coding: utf-8

import os
import requests
from datetime import datetime, timezone
from .config import WhatsAppServiceConfig

BASE_URL = "https://graph.facebook.com"

def get_db():
    try:
        from apps.extensions import db
        return db
    except:
        from app import db
        return db

def send_text_message(recipient, message):
    # ✅ توحيد الرقم
    recipient = ''.join(filter(str.isdigit, recipient))
    
    phone_id = WhatsAppServiceConfig.get_phone_number_id()
    token = WhatsAppServiceConfig.get_whatsapp_token()
    version = WhatsAppServiceConfig.get_api_version()

    url = f"{BASE_URL}/{version}/{phone_id}/messages"
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
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        res_data = response.json() if response.content else {}
        
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
            sender_number=phone_id,
            recipient_number=recipient,
            content=message,
            status=status
        )
        db.session.add(log_entry)

        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=recipient).first()
        if contact:
            contact.last_message = message
            contact.last_timestamp = datetime.now(timezone.utc)
        else:
            new_contact = WhatsAppCustomerContact(
                phone=recipient,
                name=f"عميل ({recipient})",
                last_message=message,
                last_timestamp=datetime.now(timezone.utc),
                unread_count=0
            )
            db.session.add(new_contact)
            
        db.session.commit()

        if 200 <= response.status_code < 300:
            return True, res_data
        else:
            return False, response.text

    except requests.exceptions.Timeout:
        return False, "Request to WhatsApp API timed out."
    except Exception as e:
        try:
            db = get_db()
            db.session.rollback()
        except Exception:
            pass
        return False, str(e)
