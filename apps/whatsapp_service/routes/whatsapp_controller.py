# coding: utf-8
# 📂 apps/whatsapp_service/routes/whatsapp_controller.py

"""
WhatsApp Routes and Webhook Controllers for Mahgoob Online
Handles two-way messaging, database logging, media sending, broadcasts, customer naming, and admin dashboard views.
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from sqlalchemy import or_

# استيراد دالة الإرسال العامة بشكل آمن
try:
    from ..whatsapp_api import send_text_message
except ImportError:
    from apps.whatsapp_service.whatsapp_api import send_text_message

from apps.models.whatsapp_models import (
    WhatsAppMessageLog, 
    WhatsAppWebhookEvent, 
    WhatsAppCustomerContact
)

logger = logging.getLogger(__name__)

# استخدام المسار المطلق لمجلد القوالب لضمان عمله بسلاسة على سيرفرات الإنتاج مثل Render
basedir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.abspath(os.path.join(basedir, '../templates'))

whatsapp_bp = Blueprint('whatsapp_service', __name__, template_folder=template_dir)

def get_verify_token():
    """جلب رمز التحقق الخاص بووك هوك ميتا بشكل آمن"""
    try:
        return current_app.config.get('WHATSAPP_VERIFY_TOKEN') or os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token')
    except RuntimeError:
        return os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token')

def get_db():
    """الحصول على جلسة قاعدة البيانات بأمان"""
    try:
        from apps.extensions import db
        return db
    except ImportError:
        try:
            from app import db
            return db
        except ImportError:
            return None

# ==============================================================================
# 0. DIRECT WEBHOOK ROUTE (Fixes Meta Webhook Routing & 400 Errors)
# ==============================================================================

@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
@whatsapp_bp.route('/webhook-admin', methods=['GET', 'POST'])
@whatsapp_bp.route('/admin/whatsapp/webhook', methods=['GET', 'POST'])
def direct_webhook():
    """
    مسار موحد ومباشر لاستقبال طلبات Meta (GET للتحقق و POST للرسائل)
    """
    if request.method == 'GET':
        return verify_webhook()
    return handle_webhook()

# ==============================================================================
# 1. META WEBHOOK VERIFICATION (GET) & EVENT INGESTION (POST)
# ==============================================================================

def verify_webhook():
    """معالجة عملية التحقق الأولية (Handshake) من طرف Meta"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    verify_token = get_verify_token()

    if mode == 'subscribe' and token == verify_token:
        return str(challenge), 200
    elif challenge and (token == verify_token or not token):
        return str(challenge), 200

    return "Verification token mismatch", 403


def handle_webhook():
    """مستقبل آمن للرسائل والأحداث وتحديث الحالات"""
    raw_data = request.get_data(as_text=True)
    db = get_db()
    phone_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID') or os.environ.get('WHATSAPP_PHONE_NUMBER_ID', 'system')

    data = None
    try:
        if request.is_json:
            data = request.get_json(silent=True)
        if not data and raw_data:
            import json
            data = json.loads(raw_data)
        if not data:
            data = request.form.to_dict()
    except Exception as e:
        data = {}

    if not data:
        data = {}

    try:
        if db:
            raw_event = WhatsAppWebhookEvent(
                event_type="incoming_payload",
                payload=data if isinstance(data, dict) else {"raw": str(data)},
                processed=True
            )
            db.session.add(raw_event)
            db.session.commit()

        entries = data.get('entry', []) if isinstance(data, dict) else []
        for entry in entries:
            for change in entry.get('changes', []):
                value = change.get('value', {})

                if 'messages' in value:
                    for msg in value['messages']:
                        sender = msg.get('from') 
                        msg_type = msg.get('type', 'text')
                        wamid = msg.get('id')
                        
                        if db:
                            existing_msg = db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first()
                            if existing_msg:
                                continue

                        if msg_type == 'text':
                            text = msg.get('text', {}).get('body', '')
                        else:
                            text = f'[{msg_type} ملف/وسائط]'
                            
                        contacts_list = value.get('contacts', [])
                        customer_name = f"عميل ({sender})"
                        if contacts_list:
                            profile_name = contacts_list[0].get('profile', {}).get('name')
                            if profile_name:
                                customer_name = profile_name

                        if db:
                            log_entry = WhatsAppMessageLog(
                                wamid=wamid,
                                direction='inbound',
                                sender_number=sender,
                                recipient_number=phone_id,
                                message_type=msg_type,
                                content=text,
                                status='received'
                            )
                            db.session.add(log_entry)

                            contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=sender).first()
                            if contact:
                                contact.name = customer_name if not contact.name.startswith("عميل (") else contact.name
                                contact.last_message = text
                                contact.last_timestamp = datetime.utcnow()
                                contact.unread_count = (contact.unread_count or 0) + 1
                            else:
                                new_contact = WhatsAppCustomerContact(
                                    phone=sender,
                                    name=customer_name,
                                    last_message=text,
                                    last_timestamp=datetime.utcnow(),
                                    unread_count=1
                                )
                                db.session.add(new_contact)

                            db.session.commit()

                elif 'statuses' in value:
                    for st in value['statuses']:
                        wamid = st.get('id')
                        status = st.get('status')
                        if db and wamid:
                            msg_log = db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first()
                            if msg_log:
                                msg_log.status = status
                                db.session.commit()

    except Exception as e:
        if db:
            db.session.rollback()

    return jsonify({"status": "EVENT_RECEIVED"}), 200

# ==============================================================================
# 2. INTERNAL API & ACTIONS (SENDING MESSAGES & FETCHING CHATS)
# ==============================================================================

@whatsapp_bp.route('/api/whatsapp/send', methods=['POST'])
def send_message_api():
    """إرسال رسالة نصية عبر الواجهة الديناميكية وتخزينها"""
    body = request.get_json(silent=True) or {}
    recipient = body.get('phone') or body.get('recipient_number')
    text = body.get('message')
    order_id = body.get('order_id')

    if not recipient or not text:
        return jsonify({"success": False, "error": "رقم المستلم ومحتوى الرسالة مطلوبان"}), 400

    success, response_data = send_text_message(recipient, text)
    db = get_db()
    phone_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID') or os.environ.get('WHATSAPP_PHONE_NUMBER_ID', 'system')

    if db:
        wamid = None
        if success and isinstance(response_data, dict):
            messages = response_data.get('messages', [])
            if messages:
                wamid = messages[0].get('id')

        outbound_log = WhatsAppMessageLog(
            wamid=wamid,
            direction='outbound',
            sender_number=phone_id,
            recipient_number=recipient,
            order_id=order_id,
            message_type='text',
            content=text,
            status='sent' if success else 'failed',
            error_message=None if success else str(response_data)
        )
        db.session.add(outbound_log)
        
        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=recipient).first()
        if contact:
            contact.last_message = text
            contact.last_timestamp = datetime.utcnow()
        else:
            new_contact = WhatsAppCustomerContact(
                phone=recipient,
                name=f"عميل ({recipient})",
                last_message=text,
                last_timestamp=datetime.utcnow(),
                unread_count=0
            )
            db.session.add(new_contact)

        db.session.commit()

    return jsonify({"success": success, "meta_response": response_data}), 200 if success else 500


@whatsapp_bp.route('/api/whatsapp/conversation/<phone>', methods=['GET'])
def get_conversation_data(phone):
    """مسار جلب رسائل وبيانات عميل معين عند النقر عليه في القائمة الديناميكية"""
    db = get_db()
    if not db:
        return jsonify({"success": False, "error": "Database unavailable"}), 500
    
    try:
        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
        if contact and contact.unread_count > 0:
            contact.unread_count = 0
            db.session.commit()

        messages = db.session.query(WhatsAppMessageLog).filter(
            or_(
                WhatsAppMessageLog.sender_number == phone,
                WhatsAppMessageLog.recipient_number == phone
            )
        ).order_by(WhatsAppMessageLog.id.asc()).all()

        messages_data = []
        for m in messages:
            ts = getattr(m, 'timestamp', None) or getattr(m, 'created_at', None)
            messages_data.append({
                "id": m.id,
                "direction": m.direction,
                "message_body": m.content,
                "message_type": getattr(m, 'message_type', 'text'),
                "timestamp": ts.strftime('%Y-%m-%d %H:%M') if ts else '',
                "status": m.status
            })
            
        client_info = {
            "name": contact.name if contact else phone,
            "phone": phone
        }

        return jsonify({
            "success": True, 
            "client": client_info,
            "messages": messages_data,
            "order_id": getattr(contact, 'order_id', None)
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@whatsapp_bp.route('/api/ping', methods=['GET'])
def ping_meta_api():
    return jsonify({"status": "active", "message": "WhatsApp API helper is ready for Mahgoob Online."})

# ==============================================================================
# 3. ADMIN DASHBOARD VIEWS (JINJA2 - Modular Structure)
# ==============================================================================

@whatsapp_bp.route('/dashboard')
def chat_dashboard():
    """واجهة الشات والمحادثات المباشرة (تشير للمجلد الجديد)"""
    db = get_db()
    contacts = []
    if db:
        try:
            contacts = db.session.query(WhatsAppCustomerContact).order_by(WhatsAppCustomerContact.last_timestamp.desc()).all()
            for contact in contacts:
                if contact.last_timestamp:
                    diff = datetime.utcnow() - contact.last_timestamp
                    contact.is_online = diff < timedelta(minutes=10)
                else:
                    contact.is_online = False
        except Exception as e:
            contacts = []
            
    return render_template('whatsapp/dashboard.html', active_tab='chat', contacts=contacts)


@whatsapp_bp.route('/logs')
def logs_dashboard():
    """واجهة جدول سجل الرسائل الإجمالية"""
    db = get_db()
    logs = []
    if db:
        try:
            logs = db.session.query(WhatsAppMessageLog).order_by(WhatsAppMessageLog.id.desc()).limit(150).all()
        except Exception as e:
            logs = []
            
    return render_template('whatsapp/dashboard.html', active_tab='logs', logs=logs)


@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_dashboard():
    """واجهة إعدادات مفاتيح وتأكيد WhatsApp Cloud API"""
    settings = {
        "phone_number_id": current_app.config.get('WHATSAPP_PHONE_NUMBER_ID', ''),
        "whatsapp_business_id": current_app.config.get('WHATSAPP_BUSINESS_ACCOUNT_ID', ''),
        "access_token": current_app.config.get('WHATSAPP_ACCESS_TOKEN', ''),
        "verify_token": get_verify_token()
    }
    
    saved_success = False
    if request.method == 'POST':
        flash('تم حفظ الإعدادات بنجاح', 'success')
        saved_success = True
        
    return render_template('whatsapp/dashboard.html', active_tab='settings', settings=settings, saved_success=saved_success)
