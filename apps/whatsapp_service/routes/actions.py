# coding: utf-8
# 📂 apps/whatsapp_service/routes/actions.py

import os
from datetime import datetime
from flask import request, jsonify, current_app, redirect, url_for, flash
from sqlalchemy import or_

try:
    from ..whatsapp_api import send_text_message
except ImportError:
    from apps.whatsapp_service.whatsapp_api import send_text_message

from apps.models.whatsapp_models import (
    WhatsAppMessageLog,
    WhatsAppCustomerContact
)
from apps.extensions import db
from . import whatsapp_bp


@whatsapp_bp.route('/send_message', methods=['POST'])
def send_message_htmx():
    """إرسال رسالة عبر HTMX لإضافتها فوراً بدون وميض وبدون إعادة تحميل الصفحة"""
    phone = request.form.get('phone')
    message_content = request.form.get('message')
    
    if not phone or not message_content:
        return '<div class="text-red-500 text-xs p-2">رقم الهاتف أو نص الرسالة مفقود.</div>', 400

    success, response_data = send_text_message(phone, message_content)
    
    wamid = None
    if success and isinstance(response_data, dict):
        messages_meta = response_data.get('messages', [])
        if messages_meta:
            wamid = messages_meta[0].get('id')

    phone_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID') or os.environ.get('WHATSAPP_PHONE_NUMBER_ID', 'system')
    
    with db.session.no_autoflush:
        if wamid:
            existing_log = db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first()
            if existing_log:
                wamid = None

        outbound_log = WhatsAppMessageLog(
            wamid=wamid,
            direction='outbound',
            sender_number=phone_id,
            recipient_number=phone,
            message_type='text',
            content=message_content,
            status='sent' if success else 'failed'
        )
        db.session.add(outbound_log)

        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
        if contact:
            contact.last_message = message_content
            contact.last_timestamp = datetime.utcnow()
        
        db.session.commit()

    current_time_str = datetime.utcnow().strftime('%I:%M %p')
    return f"""
    <div class="flex flex-col items-end mb-3 message-bubble">
      <div class="max-w-[70%] bg-[#632C8F] text-white rounded-2xl px-4 py-3 shadow-sm text-sm">
        <p class="leading-relaxed">{message_content}</p>
        <div class="flex items-center justify-end gap-1 mt-1 text-[10px] text-purple-200">
          <span>{current_time_str}</span>
          <i class="fa-solid fa-check-double text-[#D4AF37] text-[10px]"></i>
        </div>
      </div>
    </div>
    """


@whatsapp_bp.route('/update_contact_name/<int:contact_id>', methods=['POST'])
def update_contact_name(contact_id):
    """تعديل اسم العميل مباشرة من لوحة التحكم وحفظه"""
    contact = db.session.query(WhatsAppCustomerContact).get_or_404(contact_id)
    new_name = request.form.get('name')
    
    if new_name:
        contact.name = new_name.strip()
        db.session.commit()
        
    return f'<span class="text-sm font-bold text-slate-800">{contact.name}</span>'


@whatsapp_bp.route('/get_latest_messages/<int:contact_id>', methods=['GET'])
def get_latest_messages(contact_id):
    """جلب الرسائل الجديدة لتحديث الشاشة تلقائياً عبر HTMX Polling"""
    contact = db.session.query(WhatsAppCustomerContact).get_or_404(contact_id)
    
    if contact.unread_count > 0:
        contact.unread_count = 0
        db.session.commit()

    messages = db.session.query(WhatsAppMessageLog).filter(
        or_(
            WhatsAppMessageLog.sender_number == contact.phone,
            WhatsAppMessageLog.recipient_number == contact.phone
        )
    ).order_by(WhatsAppMessageLog.timestamp.asc()).all()

    html_output = ""
    for m in messages:
        is_outgoing = m.direction == 'outbound'
        time_str = m.timestamp.strftime('%I:%M %p') if m.timestamp else ''
        if is_outgoing:
            html_output += f"""
            <div class="flex flex-col items-end mb-3">
              <div class="max-w-[70%] bg-[#632C8F] text-white rounded-2xl px-4 py-3 shadow-sm text-sm">
                <p class="leading-relaxed">{m.content}</p>
                <div class="flex items-center justify-end gap-1 mt-1 text-[10px] text-purple-200">
                  <span>{time_str}</span>
                  <i class="fa-solid fa-check-double text-[#D4AF37] text-[10px]"></i>
                </div>
              </div>
            </div>
            """
        else:
            html_output += f"""
            <div class="flex flex-col items-start mb-3">
              <div class="max-w-[70%] bg-white border border-slate-200 text-slate-800 rounded-2xl px-4 py-3 shadow-sm text-sm">
                <p class="leading-relaxed">{m.content}</p>
                <div class="flex items-center gap-1 mt-1 text-[10px] text-slate-400">
                  <span>{time_str}</span>
                </div>
              </div>
            </div>
            """
    return html_output


@whatsapp_bp.route('/send_bulk_broadcast', methods=['POST'])
def send_bulk_broadcast():
    """إرسال حملة رسائل جماعية للعملاء مع دعم التوجيه و JSON"""
    target = request.form.get('target_audience', 'all')
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
        
    flash(f"✅ تم إرسال الحملة الجماعية بنجاح إلى {sent_count} عميل عبر محجوب أونلاين!", "success")
    return redirect(url_for('whatsapp_service.chat_dashboard'))
