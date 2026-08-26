# coding: utf-8
# 📂 apps/whatsapp_service/whatsapp_api.py

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
    # ✅ توحيد الرقم (إزالة + وأي أحرف غير رقمية)
    recipient = ''.join(filter(str.isdigit, recipient))
    
    phone_id = WhatsAppServiceConfig.get_phone_number_id()
    token = WhatsAppServiceConfig.get_whatsapp_token()
    version = WhatsAppServiceConfig.get_api_version() or "v21.0"

    # 🛑 فحص أمان هام جداً: التحقق من توفر بيانات الاعتماد
    if not phone_id or not token:
        print(f"❌ CRITICAL WHATSAPP ERROR: Missing Phone ID ({phone_id}) or Access Token ({token})!")
        return False, "Missing WhatsApp API credentials (Token or Phone ID)."

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
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        res_data = response.json() if response.content else {}
        
        db = get_db()
        from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppCustomerContact
        
        wamid = None
        try:
            wamid = res_data.get('messages', [{}])[0].get('id')
        except Exception:
            pass
            
        status = 'sent' if 200 <= response.status_code < 300 else 'failed'
        
        # طباعة حالة الإرسال في اللوقز للتشخيص الفوري
        if status == 'failed':
            print(f"❌ WHATSAPP API FAILED: Status {response.status_code} - Response: {response.text}")
        else:
            print(f"✅ WHATSAPP API SUCCESS: Message sent to {recipient} (Wamid: {wamid})")

        log_entry = WhatsAppMessageLog(
            wamid=wamid,
            direction='outbound',
            sender_number=str(phone_id),
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
        print("❌ WHATSAPP API ERROR: Request timed out.")
        return False, "Request to WhatsApp API timed out."
    except Exception as e:
        print(f"❌ WHATSAPP API EXCEPTION: {str(e)}")
        try:
            db = get_db()
            db.session.rollback()
        except Exception:
            pass
        return False, str(e)


def send_media_message(recipient, media_type, media_url, caption=None, filename=None):
    """
    ✅ دالة إرسال الوسائط (صور، فيديو، صوت، مستندات)
    """
    recipient = ''.join(filter(str.isdigit, recipient))
    
    phone_id = WhatsAppServiceConfig.get_phone_number_id()
    token = WhatsAppServiceConfig.get_whatsapp_token()
    version = WhatsAppServiceConfig.get_api_version() or "v21.0"

    if not phone_id or not token:
        print(f"❌ CRITICAL WHATSAPP ERROR (Media): Missing Phone ID or Token!")
        return False, "Missing WhatsApp API credentials."

    url = f"{BASE_URL}/{version}/{phone_id}/messages"

    media_payload = {"link": media_url}
    if filename and media_type == 'document':
        media_payload["filename"] = filename

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": media_type,
        media_type: media_payload
    }
    
    if caption and media_type in ['image', 'video']:
        payload[media_type]["caption"] = caption

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        res_data = response.json() if response.content else {}
        
        db = get_db()
        from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppCustomerContact
        
        wamid = None
        try:
            wamid = res_data.get('messages', [{}])[0].get('id')
        except Exception:
            pass
            
        status = 'sent' if 200 <= response.status_code < 300 else 'failed'
        display_content = caption if caption else (f"[{media_type}]")

        log_entry = WhatsAppMessageLog(
            wamid=wamid,
            direction='outbound',
            sender_number=str(phone_id),
            recipient_number=recipient,
            content=display_content,
            message_type=media_type,
            media_url=media_url,
            status=status
        )
        db.session.add(log_entry)

        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=recipient).first()
        if contact:
            contact.last_message = display_content
            contact.last_timestamp = datetime.now(timezone.utc)
        else:
            new_contact = WhatsAppCustomerContact(
                phone=recipient,
                name=f"عميل ({recipient})",
                last_message=display_content,
                last_timestamp=datetime.now(timezone.utc),
                unread_count=0
            )
            db.session.add(new_contact)
            
        db.session.commit()

        if 200 <= response.status_code < 300:
            return True, res_data
        else:
            print(f"❌ WHATSAPP API ERROR (Media): Status {response.status_code} - Response: {response.text}")
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
