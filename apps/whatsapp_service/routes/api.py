# coding: utf-8
# 📂 apps/whatsapp_service/routes/api.py

import os
from flask import request, jsonify, current_app
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

DEFAULT_QUICK_TEMPLATES = [
    {"id": 1, "title": "ترحيب بالعميل", "content": "مرحباً بك في منصة محجوب أونلاين! كيف يمكننا خدمة طلبك وتجربتك التسوقية اليوم؟ 🛍️✨"},
    {"id": 2, "title": "تأكيد الطلب", "content": "تم استلام طلبكم بنجاح في محجوب أونلاين ✅ وسيتم تجهيزه وشحنه في أقرب وقت."},
    {"id": 3, "title": "متابعة الشحن", "content": "طلبك قيد التوصيل حالياً، وسيتواصل معك مندوب الشحن لتسليم الطلب قريباً."},
    {"id": 4, "title": "خدمة الدعم الفني", "content": "نحن هنا لمساعدتك! إذا كان لديك أي استفسار حول المنتجات أو الطلبات، تفضل بطرحه."}
]


@whatsapp_bp.route('/api/templates', methods=['GET'])
def get_quick_templates_api():
    return jsonify({
        "success": True,
        "platform": "محجوب أونلاين",
        "templates": DEFAULT_QUICK_TEMPLATES
    })


@whatsapp_bp.route('/api/whatsapp/conversation/<phone>', methods=['GET'])
def get_conversation_data(phone):
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
    data = request.get_json(silent=True) or {}
    phone = data.get('phone')
    message = data.get('message')
    if not phone or not message:
        return jsonify({"success": False, "error": "بيانات ناقصة"}), 400

    success, response_data = send_text_message(phone, message)
    return jsonify({"success": success, "meta_response": response_data}), 200 if success else 500


@whatsapp_bp.route('/ping')
def ping():
    return jsonify({"status": "active", "service": "WhatsApp Service", "version": "1.0", "platform": "محجوب أونلاين"})
