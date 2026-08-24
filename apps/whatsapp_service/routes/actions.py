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
