# coding: utf-8
# 📂 apps/whatsapp_service/routes/api.py

"""
WhatsApp JSON APIs
Handles real-time polling data retrieval and AJAX live message sending.
"""

from flask import request, jsonify
from sqlalchemy import or_
from . import whatsapp_bp
from apps.whatsapp_service.whatsapp_api import send_text_message
from apps.models.whatsapp_models import (
    WhatsAppMessageLog,
    WhatsAppCustomerContact
)
from apps.extensions import db


@whatsapp_bp.route('/api/whatsapp/conversation/<phone>', methods=['GET'])
def get_conversation_data(phone):
    """جلب رسائل عميل معين بصيغة JSON لدعم المزامنة الحية التلقائية"""
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
            "timestamp": ts.strftime('%Y-%m-%d %H:%M:%S') if ts else '',
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
    """إرسال رسالة مباشرة وفورية عبر AJAX JSON"""
    data = request.get_json(silent=True) or {}
    phone = data.get('phone')
    message = data.get('message')
    
    if not phone or not message:
        return jsonify({"success": False, "error": "بيانات ناقصة"}), 400

    success, response_data = send_text_message(phone, message)
    return jsonify({"success": success, "meta_response": response_data}), (200 if success else 500)
