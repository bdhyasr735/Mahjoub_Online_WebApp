# coding: utf-8

import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from apps.extensions import db, csrf
from apps.models.whatsapp_models import (
    WhatsAppCustomerContact, 
    WhatsAppMessageLog, 
    WhatsAppSettings
)
from apps.services.whatsapp_api import send_text_message
from apps.config import WhatsAppServiceConfig

whatsapp_bp = Blueprint('whatsapp_bp', __name__, template_folder='templates')

@whatsapp_bp.route('/chat')
def chat_dashboard():
    contacts = WhatsAppCustomerContact.query.order_by(WhatsAppCustomerContact.last_timestamp.desc()).all()
    selected_phone = request.args.get('phone')
    messages = []
    active_contact = None

    if selected_phone:
        active_contact = WhatsAppCustomerContact.query.filter_by(phone=selected_phone).first()
        if active_contact:
            # تحديث عدد الرسائل غير المقروءة إلى صفر عند فتح المحادثة
            active_contact.unread_count = 0
            db.session.commit()
            
        messages = WhatsAppMessageLog.query.filter(
            (WhatsAppMessageLog.sender_number == selected_phone) | 
            (WhatsAppMessageLog.recipient_number == selected_phone)
        ).order_by(WhatsAppMessageLog.timestamp.asc()).all()
    elif contacts:
        active_contact = contacts[0]
        selected_phone = active_contact.phone
        messages = WhatsAppMessageLog.query.filter(
            (WhatsAppMessageLog.sender_number == selected_phone) | 
            (WhatsAppMessageLog.recipient_number == selected_phone)
        ).order_by(WhatsAppMessageLog.timestamp.asc()).all()

    return render_template(
        'whatsapp/chat_dashboard.html',
        contacts=contacts,
        active_contact=active_contact,
        messages=messages,
        selected_phone=selected_phone
    )

@whatsapp_bp.route('/send-message', methods=['POST'])
@csrf.exempt
def send_message_htmx():
    recipient = request.form.get('recipient') or request.json.get('recipient')
    message = request.form.get('message') or request.json.get('message')

    if not recipient or not message:
        return jsonify({"success": False, "error": "المستلم أو نص الرسالة غير موجود."}), 400

    success, result = send_text_message(recipient, message)
    
    if success:
        if request.headers.get('HX-Request'):
            # جلب الرسالة الأخيرة لعرضها مباشرة عبر HTMX
            new_msg = WhatsAppMessageLog.query.filter_by(recipient_number=recipient).order_by(WhatsAppMessageLog.id.desc()).first()
            return render_template('whatsapp/_message_bubble.html', msg=new_msg)
        return jsonify({"success": True, "result": result})
    else:
        return jsonify({"success": False, "error": str(result)}), 500

@whatsapp_bp.route('/start-new-chat', methods=['POST'])
@csrf.exempt
def start_new_chat():
    phone = request.form.get('phone')
    name = request.form.get('name', f"عميل ({phone})")

    if not phone:
        return redirect(url_for('whatsapp_bp.chat_dashboard'))

    contact = WhatsAppCustomerContact.query.filter_by(phone=phone).first()
    if not contact:
        contact = WhatsAppCustomerContact(
            phone=phone,
            name=name,
            last_message="",
            last_timestamp=datetime.utcnow(),
            unread_count=0
        )
        db.session.add(contact)
        db.session.commit()

    return redirect(url_for('whatsapp_bp.chat_dashboard', phone=phone))

@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_view():
    if request.method == 'POST':
        phone_id = request.form.get('whatsapp_phone_number_id')
        token = request.form.get('whatsapp_token')
        verify_token = request.form.get('whatsapp_verify_token')
        api_version = request.form.get('whatsapp_api_version', 'v17.0')

        WhatsAppSettings.set_setting('WHATSAPP_PHONE_NUMBER_ID', phone_id)
        WhatsAppSettings.set_setting('WHATSAPP_TOKEN', token)
        WhatsAppSettings.set_setting('WHATSAPP_VERIFY_TOKEN', verify_token)
        WhatsAppSettings.set_setting('WHATSAPP_API_VERSION', api_version)

        return redirect(url_for('whatsapp_bp.settings_view'))

    settings = {
        'phone_id': WhatsAppServiceConfig.get_phone_number_id(),
        'token': WhatsAppServiceConfig.get_whatsapp_token(),
        'verify_token': WhatsAppServiceConfig.get_verify_token(),
        'api_version': WhatsAppServiceConfig.get_api_version()
    }
    return render_template('whatsapp/settings_view.html', settings=settings)

@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
@csrf.exempt
def whatsapp_webhook_handler():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        verify_token = WhatsAppServiceConfig.get_verify_token()
        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                return challenge, 200
            else:
                return 'Verification token mismatch', 403
        return 'Hello WhatsApp Webhook', 200

    elif request.method == 'POST':
        data = request.json
        try:
            entries = data.get('entry', [])
            for entry in entries:
                changes = entry.get('changes', [])
                for change in changes:
                    value = change.get('value', {})
                    
                    # معالجة الرسائل الواردة
                    messages = value.get('messages', [])
                    for msg in messages:
                        sender = msg.get('from')
                        msg_body = msg.get('text', {}).get('body', '')
                        wamid = msg.get('id')

                        log_entry = WhatsAppMessageLog(
                            wamid=wamid,
                            direction='inbound',
                            sender_number=sender,
                            recipient_number=WhatsAppServiceConfig.get_phone_number_id(),
                            content=msg_body,
                            status='received'
                        )
                        db.session.add(log_entry)

                        contact = WhatsAppCustomerContact.query.filter_by(phone=sender).first()
                        if contact:
                            contact.last_message = msg_body
                            contact.last_timestamp = datetime.utcnow()
                            contact.unread_count = (contact.unread_count or 0) + 1
                        else:
                            new_contact = WhatsAppCustomerContact(
                                phone=sender,
                                name=f"عميل ({sender})",
                                last_message=msg_body,
                                last_timestamp=datetime.utcnow(),
                                unread_count=1
                            )
                            db.session.add(new_contact)
                        
                        db.session.commit()

                    # معالجة حالات الرسائل (Sent, Delivered, Read)
                    statuses = value.get('statuses', [])
                    for st in statuses:
                        wamid = st.get('id')
                        status_type = st.get('status') # sent, delivered, read
                        msg_log = WhatsAppMessageLog.query.filter_by(wamid=wamid).first()
                        if msg_log:
                            msg_log.status = status_type
                            db.session.commit()

        except Exception as e:
            current_app.logger.error(f"Webhook error: {str(e)}")

        return jsonify({"status": "success"}), 200
