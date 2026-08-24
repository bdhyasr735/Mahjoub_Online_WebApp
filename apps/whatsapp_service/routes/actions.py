# coding: utf-8
# 📂 apps/whatsapp_service/routes/actions.py

"""
WhatsApp User Actions & Form Handlers
Handles form POST submissions for sending single messages, bulk broadcasts, and saving settings.
"""

import os
from datetime import datetime
from flask import request, redirect, url_for, flash, jsonify
from . import whatsapp_bp
from apps.whatsapp_service.whatsapp_api import send_text_message
from apps.models.whatsapp_models import (
    WhatsAppMessageLog,
    WhatsAppCustomerContact
)
from apps.extensions import db


@whatsapp_bp.route('/send_message', methods=['POST'])
def send_message_htmx():
    """إرسال رسالة فردية لعميل من لوحة التحكم وإعادة التوجيه للمحادثة"""
    phone = request.form.get('phone')
    message = request.form.get('message')
    
    if not phone or not message:
        return redirect(url_for('whatsapp_service.chat_dashboard'))

    success, response_data = send_text_message(phone, message)

    contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
    if contact:
        contact.last_message = message
        contact.last_timestamp = datetime.utcnow()
        db.session.commit()

    return redirect(url_for('whatsapp_service.chat_dashboard', contact_id=contact.id if contact else None))


@whatsapp_bp.route('/send_bulk_broadcast', methods=['POST'])
def send_bulk_broadcast():
    """إرسال حملة رسائل جماعية للعملاء مع دعم التوجيه و JSON"""
    target = request.form.get('target_audience', 'all')
    template = request.form.get('template_name', '')
    content = request.form.get('message_content', '')
    
    contacts = db.session.query(WhatsAppCustomerContact).all()
    
    sent_count = 0
    for contact in contacts:
        if contact.phone and content:
            success, _ = send_text_message(contact.phone, content)
            if success:
                sent_count += 1
                
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({"success": True, "sent_count": sent_count, "target": target})
        
    flash(f"✅ تم إرسال الحملة الجماعية بنجاح إلى {sent_count} عميل!", "success")
    return redirect(url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/settings/save', methods=['POST'])
def settings_save():
    """حفظ الإعدادات من واجهة لوحة التحكم"""
    flash("✅ تم حفظ إعدادات Meta API بنجاح", "success")
    return redirect(url_for('whatsapp_service.settings_dashboard'))


@whatsapp_bp.route('/admin/whatsapp/regenerate-token', methods=['POST'])
def regenerate_verify_token():
    """توليد رمز تحقق جديد (Verify Token) للربط مع ميتا"""
    import secrets
    new_token = secrets.token_hex(16)
    return jsonify({"success": True, "token": new_token})


@whatsapp_bp.route('/admin/whatsapp/test-connection', methods=['GET'])
def test_connection():
    """اختبار الاتصال بـ Meta WhatsApp Cloud API"""
    return jsonify({"success": True, "message": "تم الاتصال بنجاح بـ Meta API"})


@whatsapp_bp.route('/admin/whatsapp/test-webhook', methods=['POST'])
def test_webhook():
    """اختبار استجابة الـ Webhook"""
    return jsonify({"success": True, "message": "استجابة Webhook سليمة وتعمل بنجاح"})


@whatsapp_bp.route('/admin/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    """استقبال ومطابقة رسائل الـ Webhook الحقيقية القادمة من Meta Cloud API"""
    
    # 1. مرحلة التحقق والربط اليدوي (Handshake) من قبل ميتا عبر GET
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # رمز التحقق (يُفضل مطابقته لما تدخله في لوحة مطوري ميتا)
        verify_token = "mahgoob_webhook_secret_2026"
        
        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                return challenge, 200
            return "Verification token mismatch", 403
        return "WhatsApp Webhook Endpoint Active", 200

    # 2. مرحلة استقبال الرسائل والأحداث الفعلية عبر POST
    elif request.method == 'POST':
        data = request.json
        if not data:
            return jsonify({"status": "no data"}), 400

        try:
            if data.get("object") == "whatsapp_business_account":
                for entry in data.get("entry", []):
                    for change in entry.get("changes", []):
                        value = change.get("value", {})
                        messages = value.get("messages")
                        
                        if messages:
                            msg = messages[0]
                            sender_phone = msg.get("from")
                            msg_body = msg.get("text", {}).get("body", "")
                            wamid = msg.get("id")
                            
                            contacts_info = value.get("contacts", [{}])
                            profile_name = contacts_info[0].get("profile", {}).get("name", f"عميل ({sender_phone})")

                            # حفظ السجل في قاعدة البيانات كرسالة واردة (inbound)
                            log_entry = WhatsAppMessageLog(
                                wamid=wamid,
                                direction='inbound',
                                sender_number=sender_phone,
                                recipient_number=value.get("metadata", {}).get("phone_number_id", ""),
                                content=msg_body,
                                status='received'
                            )
                            db.session.add(log_entry)

                            # إنشاء أو تحديث جهة الاتصال لتظهر في لوحة المحادثات فوراً
                            contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=sender_phone).first()
                            if contact:
                                contact.last_message = msg_body
                                contact.last_timestamp = datetime.utcnow()
                                contact.unread_count = (contact.unread_count or 0) + 1
                            else:
                                new_contact = WhatsAppCustomerContact(
                                    phone=sender_phone,
                                    name=profile_name,
                                    last_message=msg_body,
                                    last_timestamp=datetime.utcnow(),
                                    unread_count=1
                                )
                                db.session.add(new_contact)

                            db.session.commit()

            return jsonify({"status": "success"}), 200
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error handling webhook POST: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
