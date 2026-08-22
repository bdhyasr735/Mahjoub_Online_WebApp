# coding: utf-8
# 📂 apps/whatsapp_service/whatsapp_api.py

import os
import requests
from flask import Blueprint, request, jsonify, render_template
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

whatsapp_bp = Blueprint('whatsapp', __name__, url_prefix='/api/whatsapp')

PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
VERSION = os.getenv("VERSION", "v20.0")
BASE_URL = "https://graph.facebook.com"

def get_db():
    try:
        from app import db
        return db
    except:
        from apps.extensions import db
        return db

# ==========================================
# 1. الدالة العامة لإرسال رسائل النص (مستقلة لتجنب أخطاء الاستيراد)
# ==========================================
def send_text_message(recipient, message):
    """
    دالة عامة لإرسال رسائل الواتساب يمكن استدعاؤها من أي مكان في النظام
    """
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
        if response.status_code == 200:
            db = get_db()
            from apps.models.whatsapp_models import WhatsAppMessageLog
            
            res_data = response.json()
            wamid = None
            try:
                wamid = res_data.get('messages', [{}])[0].get('id')
            except:
                pass
                
            db.session.add(WhatsAppMessageLog(
                wamid=wamid,
                direction='outbound', 
                sender_number=PHONE_NUMBER_ID, 
                recipient_number=recipient, 
                content=message, 
                status='sent'
            ))
            db.session.commit()
            return True, res_data
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)


# ==========================================
# 2. تحديث اسم العميل يدوياً
# ==========================================
@whatsapp_bp.route('/update-contact-name', methods=['POST'])
def update_contact_name():
    db = get_db()
    data = request.get_json() or {}
    phone = data.get('phone')
    new_name = data.get('name')
    
    from apps.models.whatsapp_models import WhatsAppCustomerContact
    contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
    if contact:
        contact.name = new_name
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "غير موجود"}), 404


# ==========================================
# 3. معالجة الـ Webhook (دعم الوسائط ومنع التكرار)
# ==========================================
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
                # فحص التكرار
                if db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first():
                    continue
                
                sender = msg.get('from')
                msg_type = msg.get('type', 'text')
                
                # استخراج المحتوى والوسائط
                content = ""
                media_id = None
                if msg_type == 'text':
                    content = msg.get('text', {}).get('body', '')
                else:
                    content = f"[{msg_type} ملف]"
                    media_id = msg.get(msg_type, {}).get('id')
                
                # حفظ الرسالة
                log_entry = WhatsAppMessageLog(
                    wamid=wamid,
                    direction='inbound',
                    sender_number=sender,
                    recipient_number=PHONE_NUMBER_ID,
                    message_type=msg_type,
                    content=content,
                    media_id=media_id
                )
                db.session.add(log_entry)
                
                # تحديث جهة الاتصال
                contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=sender).first()
                if contact:
                    contact.last_message = content
                    contact.last_timestamp = datetime.utcnow()
                else:
                    db.session.add(WhatsAppCustomerContact(phone=sender, name="عميل جديد", last_message=content))
                
                db.session.commit()
    return jsonify({'status': 'success'}), 200


# ==========================================
# 4. إرسال الرسالة من لوحة التحكم (تستعين بالدالة العامة)
# ==========================================
@whatsapp_bp.route('/send-message', methods=['POST'])
def send_dashboard_message():
    data = request.get_json() or {}
    phone = data.get('phone') or data.get('recipient_number')
    message = data.get('message')
    
    if not phone or not message:
        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400

    success, result = send_text_message(phone, message)
    
    if success:
        return jsonify({"status": "success", "result": result})
    
    return jsonify({"status": "error", "message": result}), 500