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
# 1. تحديث اسم العميل يدوياً
# ==========================================
@whatsapp_bp.route('/update-contact-name', methods=['POST'])
def update_contact_name():
    db = get_db()
    data = request.get_json()
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
# 2. معالجة الـ Webhook (دعم الوسائط ومنع التكرار)
# ==========================================
@whatsapp_bp.route('/webhook', methods=['POST'])
def receive_webhook():
    data = request.get_json()
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
# 3. إرسال الرسالة من لوحة التحكم (مع منع تكرار النقر)
# ==========================================
@whatsapp_bp.route('/send-message', methods=['POST'])
def send_dashboard_message():
    data = request.get_json()
    phone = data.get('phone')
    message = data.get('message')
    
    # هنا يتم الإرسال عبر requests
    url = f"{BASE_URL}/{VERSION}/{PHONE_NUMBER_ID}/messages"
    payload = {"messaging_product": "whatsapp", "to": phone, "type": "text", "text": {"body": message}}
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        # حفظ في قاعدة البيانات بعد نجاح الإرسال
        db = get_db()
        from apps.models.whatsapp_models import WhatsAppMessageLog
        db.session.add(WhatsAppMessageLog(
            direction='outbound', 
            sender_number=PHONE_NUMBER_ID, 
            recipient_number=phone, 
            content=message, 
            status='sent'
        ))
        db.session.commit()
        return jsonify({"status": "success"})
    
    return jsonify({"status": "error"}), response.status_code

# ... (باقي المسارات كما هي)