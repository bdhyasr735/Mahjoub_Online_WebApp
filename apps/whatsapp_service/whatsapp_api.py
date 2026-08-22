# coding: utf-8
# 📂 apps/whatsapp_service/whatsapp_api.py

import os
import requests
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

whatsapp_bp = Blueprint('whatsapp_service', __name__, url_prefix='/api/whatsapp')

PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
VERSION = os.getenv("VERSION", "v20.0")
BASE_URL = "https://graph.facebook.com"
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mahjoub_secure_webhook_token")

def get_db():
    try:
        from app import db
        return db
    except:
        from apps.extensions import db
        return db

# ==========================================
# 1. الدالة العامة لإرسال رسائل النص
# ==========================================
def send_text_message(recipient, message):
    url = f"{BASE_URL}/{VERSION}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": message}
    }
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}", 
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        
        db = get_db()
        from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppCustomerContact
        
        wamid = None
        try:
            wamid = res_data.get('messages', [{}])[0].get('id')
        except:
            pass
            
        status = 'sent' if response.status_code == 200 else 'failed'
        
        # حفظ السجل
        log_entry = WhatsAppMessageLog(
            wamid=wamid,
            direction='outbound', 
            sender_number=PHONE_NUMBER_ID, 
            recipient_number=recipient, 
            content=message, 
            status=status
        )
        db.session.add(log_entry)

        # تحديث آخر رسالة وجهة الاتصال
        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=recipient).first()
        if contact:
            contact.last_message = message
            contact.last_timestamp = datetime.utcnow()
            
        db.session.commit()

        if response.status_code == 200:
            return True, res_data
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)


# ==========================================
# 2. التحقق من الـ Webhook (GET) واستقبال الرسائل (POST)
# ==========================================
@whatsapp_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return jsonify({"status": "error", "message": "Verification token mismatch"}), 403
    return jsonify({"status": "error", "message": "Missing parameters"}), 400


@whatsapp_bp.route('/webhook', methods=['POST'])
def receive_webhook():
    data = request.get_json() or {}
    db = get_db()
    
    from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppCustomerContact
    
    for entry in data.get('entry', []):
        for change in entry.get('changes', []):
            value = change.get('value', {})
            messages = value.get('messages', [])
            
            for msg in messages:
                wamid = msg.get('id')
                if db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first():
                    continue
                
                sender = msg.get('from')
                msg_type = msg.get('type', 'text')
                
                content = ""
                media_id = None
                if msg_type == 'text':
                    content = msg.get('text', {}).get('body', '')
                else:
                    content = f"[{msg_type} ملف أو وسائط]"
                    media_id = msg.get(msg_type, {}).get('id')
                
                log_entry = WhatsAppMessageLog(
                    wamid=wamid,
                    direction='inbound',
                    sender_number=sender,
                    recipient_number=PHONE_NUMBER_ID,
                    message_type=msg_type,
                    content=content,
                    media_id=media_id,
                    status='delivered'
                )
                db.session.add(log_entry)
                
                contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=sender).first()
                if contact:
                    contact.last_message = content
                    contact.last_timestamp = datetime.utcnow()
                else:
                    db.session.add(WhatsAppCustomerContact(phone=sender, name="عميل محجوب", last_message=content, last_timestamp=datetime.utcnow()))
                
                db.session.commit()
    return jsonify({'status': 'success'}), 200


# ==========================================
# 3. جلب رسائل محادثة عميل معين
# ==========================================
@whatsapp_bp.route('/customer-messages/<phone>', methods=['GET'])
def get_customer_messages(phone):
    db = get_db()
    from apps.models.whatsapp_models import WhatsAppMessageLog
    
    logs = db.session.query(WhatsAppMessageLog).filter(
        (WhatsAppMessageLog.recipient_number == phone) | (WhatsAppMessageLog.sender_number == phone)
    ).order_by(WhatsAppMessageLog.timestamp.asc()).all()
    
    messages_data = []
    for log in logs:
        messages_data.append({
            "id": log.id,
            "direction": log.direction,
            "content": log.content,
            "message_type": getattr(log, 'message_type', 'text'),
            "status": log.status,
            "timestamp": log.timestamp.strftime('%Y-%m-%d %H:%M') if log.timestamp else ''
        })
        
    return jsonify({"success": True, "messages": messages_data})


# ==========================================
# 4. إرسال الرسالة من لوحة التحكم
# ==========================================
@whatsapp_bp.route('/send-message', methods=['POST'])
def send_message_api():
    data = request.get_json() or {}
    phone = data.get('recipient_number') or data.get('phone')
    message = data.get('message')
    
    if not phone or not message:
        return jsonify({"success": False, "error": "بيانات غير مكتملة"}), 400

    success, result = send_text_message(phone, message)
    if success:
        return jsonify({"success": True, "result": result})
    return jsonify({"success": False, "error": str(result)}), 500


# ==========================================
# 5. إرسال الوسائط والصور
# ==========================================
@whatsapp_bp.route('/send-media', methods=['POST'])
def send_media_api():
    phone = request.form.get('recipient_number')
    file = request.files.get('media')
    
    if not phone or not file:
        return jsonify({"success": False, "error": "الرجاء إرفاق الملف ورقم المستلم"}), 400

    db = get_db()
    from apps.models.whatsapp_models import WhatsAppMessageLog
    
    log_entry = WhatsAppMessageLog(
        direction='outbound',
        sender_number=PHONE_NUMBER_ID,
        recipient_number=phone,
        message_type='image',
        content=f"[صورة مرفقة: {file.filename}]",
        status='sent'
    )
    db.session.add(log_entry)
    db.session.commit()

    return jsonify({"success": True, "message": "تم إرسال الصورة بنجاح"})


# ==========================================
# 6. حملة الرسائل الجماعية (Broadcast)
# ==========================================
@whatsapp_bp.route('/broadcast', methods=['POST'])
def broadcast_message_api():
    data = request.get_json() or {}
    message = data.get('message')
    
    if not message:
        return jsonify({"success": False, "error": "محتوى الرسالة مطلوب"}), 400
        
    db = get_db()
    from apps.models.whatsapp_models import WhatsAppCustomerContact
    
    contacts = db.session.query(WhatsAppCustomerContact).all()
    success_count = 0
    
    for contact in contacts:
        success, _ = send_text_message(contact.phone, message)
        if success:
            success_count += 1
            
    return jsonify({"success": True, "sent_count": success_count})


# ==========================================
# 7. تحديث وحفظ اسم العميل يدوياً
# ==========================================
@whatsapp_bp.route('/customer/<int:contact_id>/update-name', methods=['POST'])
def update_customer_name(contact_id):
    data = request.get_json() or {}
    new_name = data.get('name')
    
    if not new_name:
        return jsonify({"success": False, "error": "الاسم الجديد مطلوب"}), 400
        
    db = get_db()
    from apps.models.whatsapp_models import WhatsAppCustomerContact
    
    contact = db.session.query(WhatsAppCustomerContact).filter_by(id=contact_id).first()
    if not contact:
        return jsonify({"success": False, "error": "العميل غير موجود"}), 404
        
    try:
        contact.name = new_name
        db.session.commit()
        return jsonify({"success": True, "message": "تم تحديث اسم العميل بنجاح"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
