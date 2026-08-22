# coding: utf-8
# 📂 apps/whatsapp_service/routes/whatsapp_controller.py

import os
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, current_app
from sqlalchemy import or_

try:
    from ..whatsapp_api import send_text_message
except ImportError:
    from apps.whatsapp_service.whatsapp_api import send_text_message

from apps.models.whatsapp_models import (
    WhatsAppMessageLog,
    WhatsAppWebhookEvent,
    WhatsAppCustomerContact
)
from apps.extensions import db

logger = logging.getLogger(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.abspath(os.path.join(basedir, '../templates'))

whatsapp_bp = Blueprint('whatsapp_service', __name__, template_folder=template_dir)


def get_verify_token():
    try:
        return current_app.config.get('WHATSAPP_VERIFY_TOKEN') or os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token')
    except RuntimeError:
        return os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token')


# =============================================================================
# 1. WEBHOOK (GET + POST)
# =============================================================================

@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
@whatsapp_bp.route('/webhook-admin', methods=['GET', 'POST'])
@whatsapp_bp.route('/admin/whatsapp/webhook', methods=['GET', 'POST'])
def direct_webhook():
    if request.method == 'GET':
        return verify_webhook()
    return handle_webhook()


def verify_webhook():
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
    data = request.get_json(silent=True) or {}
    phone_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID') or os.environ.get('WHATSAPP_PHONE_NUMBER_ID', 'system')

    try:
        entries = data.get('entry', [])
        for entry in entries:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if 'messages' in value:
                    for msg in value['messages']:
                        sender = msg.get('from')
                        msg_type = msg.get('type', 'text')
                        wamid = msg.get('id')
                        if msg_type == 'text':
                            text = msg.get('text', {}).get('body', '')
                        else:
                            text = f'[{msg_type} ملف]'
                        contacts_list = value.get('contacts', [])
                        customer_name = f"عميل ({sender})"
                        if contacts_list:
                            profile_name = contacts_list[0].get('profile', {}).get('name')
                            if profile_name:
                                customer_name = profile_name

                        # حفظ الرسالة
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

                        # تحديث أو إنشاء جهة اتصال
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
                        if wamid:
                            msg_log = db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first()
                            if msg_log:
                                msg_log.status = status
                                db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Webhook error: {e}")

    return jsonify({"status": "EVENT_RECEIVED"}), 200


# =============================================================================
# 2. DASHBOARD (الصفحة الرئيسية)
# =============================================================================

@whatsapp_bp.route('/dashboard')
def chat_dashboard():
    """عرض لوحة التحكم الرئيسية مع جميع جهات الاتصال وأول عميل محدد"""
    contacts = db.session.query(WhatsAppCustomerContact).order_by(
        WhatsAppCustomerContact.last_timestamp.desc()
    ).all()

    # تعيين حالة الاتصال (online/offline)
    for contact in contacts:
        if contact.last_timestamp:
            diff = datetime.utcnow() - contact.last_timestamp
            contact.is_online = diff < timedelta(minutes=10)
        else:
            contact.is_online = False

    # قراءة رقم العميل المحدد من الرابط (مثل ?contact_id=1)
    contact_id = request.args.get('contact_id', type=int)
    
    current_contact = None
    
    if contact_id:
        current_contact = db.session.query(WhatsAppCustomerContact).get(contact_id)
    
    if not current_contact and contacts:
        current_contact = contacts[0]
    
    messages = []
    if current_contact:
        messages = db.session.query(WhatsAppMessageLog).filter(
            or_(
                WhatsAppMessageLog.sender_number == current_contact.phone,
                WhatsAppMessageLog.recipient_number == current_contact.phone
            )
        ).order_by(WhatsAppMessageLog.timestamp.asc()).limit(50).all()

    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='chat',
        contacts=contacts,
        current_contact=current_contact,
        messages=messages
    )


# =============================================================================
# 3. HTMX ENDPOINTS (لتحديث الأجزاء ديناميكياً)
# =============================================================================

@whatsapp_bp.route('/client/<int:contact_id>/chat')
def get_chat_area(contact_id):
    """إرجاع مكون الشات فقط (للاستخدام مع HTMX)"""
    contact = db.session.query(WhatsAppCustomerContact).get(contact_id)
    if not contact:
        return "العميل غير موجود", 404

    if contact.unread_count > 0:
        contact.unread_count = 0
        db.session.commit()

    messages = db.session.query(WhatsAppMessageLog).filter(
        or_(
            WhatsAppMessageLog.sender_number == contact.phone,
            WhatsAppMessageLog.recipient_number == contact.phone
        )
    ).order_by(WhatsAppMessageLog.timestamp.asc()).limit(50).all()

    return render_template('admin/components/_chat_area.html', contact=contact, messages=messages)


@whatsapp_bp.route('/client/<int:contact_id>/details')
def get_client_details(contact_id):
    """إرجاع مكون تفاصيل العميل فقط (للاستخدام مع HTMX)"""
    contact = db.session.query(WhatsAppCustomerContact).get(contact_id)
    if not contact:
        return "العميل غير موجود", 404
    return render_template('admin/components/_client_details.html', contact=contact)


@whatsapp_bp.route('/refresh_contacts')
def refresh_contacts():
    """تحديث قائمة جهات الاتصال في الشريط الجانبي"""
    contacts = db.session.query(WhatsAppCustomerContact).order_by(
        WhatsAppCustomerContact.last_timestamp.desc()
    ).all()
    for contact in contacts:
        if contact.last_timestamp:
            diff = datetime.utcnow() - contact.last_timestamp
            contact.is_online = diff < timedelta(minutes=10)
        else:
            contact.is_online = False
    return render_template('admin/components/_sidebar_contacts.html', contacts=contacts)


@whatsapp_bp.route('/send_message', methods=['POST'])
def send_message_htmx():
    """إرسال رسالة وتحديث القائمة الجانبية (HTMX)"""
    phone = request.form.get('phone')
    message = request.form.get('message')
    if not phone or not message:
        return "بيانات ناقصة", 400

    success, response_data = send_text_message(phone, message)

    contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
    if contact:
        contact.last_message = message
        contact.last_timestamp = datetime.utcnow()
        db.session.commit()

    return refresh_contacts()


# =============================================================================
# 4. API ENDPOINTS (للاستخدام مع Fetch)
# =============================================================================

@whatsapp_bp.route('/api/whatsapp/conversation/<phone>', methods=['GET'])
def get_conversation_data(phone):
    """جلب رسائل عميل معين بصيغة JSON (للاستخدام مع JavaScript)"""
    contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
    if contact and contact.unread_count > 0:
        contact.unread_count = 0
        db.session.commit()

    messages = db.session.query(WhatsAppMessageLog).filter(
        or_(
            WhatsAppMessageLog.sender_number == phone,
            WhatsAppMessageLog.recipient_number == phone
        )
    ).order_by(WhatsAppMessageLog.timestamp.asc()).all()

    messages_data = []
    for m in messages:
        ts = getattr(m, 'timestamp', None)
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
        "messages": messages_data
    })


@whatsapp_bp.route('/api/whatsapp/send', methods=['POST'])
def send_message_api():
    """إرسال رسالة عبر JSON (للاستخدام مع JavaScript)"""
    data = request.get_json(silent=True) or {}
    phone = data.get('phone')
    message = data.get('message')
    if not phone or not message:
        return jsonify({"success": False, "error": "بيانات ناقصة"}), 400

    success, response_data = send_text_message(phone, message)
    return jsonify({"success": success, "meta_response": response_data}), 200 if success else 500


# =============================================================================
# 5. BULK BROADCAST & OTHER TABS
# =============================================================================

@whatsapp_bp.route('/send_bulk_broadcast', methods=['POST'])
def send_bulk_broadcast():
    """إرسال حملة رسائل جماعية للعملاء"""
    target = request.form.get('target_audience', 'all')
    template = request.form.get('template_name', '')
    content = request.form.get('message_content', '')
    
    contacts = []
    if target == 'all':
        contacts = db.session.query(WhatsAppCustomerContact).all()
    
    sent_count = 0
    for contact in contacts:
        if contact.phone and content:
            success, _ = send_text_message(contact.phone, content)
            if success:
                sent_count += 1
                
    return jsonify({"success": True, "sent_count": sent_count, "target": target})


@whatsapp_bp.route('/logs')
def logs_dashboard():
    logs = db.session.query(WhatsAppMessageLog).order_by(WhatsAppMessageLog.id.desc()).limit(150).all()
    return render_template('admin/whatsapp_dashboard.html', active_tab='logs', logs=logs)


@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_dashboard():
    settings = {
        "phone_number_id": current_app.config.get('WHATSAPP_PHONE_NUMBER_ID', ''),
        "whatsapp_business_id": current_app.config.get('WHATSAPP_BUSINESS_ACCOUNT_ID', ''),
        "access_token": current_app.config.get('WHATSAPP_ACCESS_TOKEN', ''),
        "verify_token": get_verify_token()
    }
    saved_success = False
    if request.method == 'POST':
        saved_success = True
    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='settings',
        settings=settings,
        saved_success=saved_success
    )


@whatsapp_bp.route('/ping')
def ping():
    return jsonify({"status": "active", "service": "WhatsApp Service", "version": "1.0"})
