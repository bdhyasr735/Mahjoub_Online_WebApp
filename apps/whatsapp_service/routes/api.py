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


@whatsapp_bp.route('/api/whatsapp/conversations', methods=['GET'])
def get_conversations_list():
    """جلب قائمة المحادثات والعملاء النشطين بصيغة JSON"""
    try:
        # استخدام last_timestamp مطابقةً لملفات الويب هوك ولوحة التحكم
        contacts = db.session.query(WhatsAppCustomerContact).order_by(
            WhatsAppCustomerContact.last_timestamp.desc()
        ).all()
        
        conversations = []
        for c in contacts:
            ts = getattr(c, 'last_timestamp', None)
            conversations.append({
                "id": c.id,
                "phone": c.phone,
                "name": c.name or c.phone,
                "last_message": c.last_message or '',
                "last_time": ts.strftime('%I:%M %p') if ts else '',
                "unread_count": getattr(c, 'unread_count', 0)
            })
        return jsonify({"success": True, "conversations": conversations})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@whatsapp_bp.route('/api/whatsapp/conversation/<phone>', methods=['GET'])
def get_conversation_data(phone):
    """جلب رسائل عميل معين بصيغة JSON لدعم المزامنة الحية التلقائية"""
    try:
        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
        if contact and getattr(contact, 'unread_count', 0) > 0:
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
                "body": m.content,
                "message_type": getattr(m, 'message_type', 'text'),
                "time": ts.strftime('%I:%M %p') if ts else '',
                "status": getattr(m, 'status', 'sent')
            })

        return jsonify({
            "success": True,
            "messages": messages_data
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@whatsapp_bp.route('/api/whatsapp/send', methods=['POST'])
def send_message_api():
    """إرسال رسالة مباشرة وفورية عبر AJAX JSON"""
    try:
        data = request.get_json(silent=True) or {}
        phone = data.get('phone')
        message = data.get('message')
        
        if not phone or not message:
            return jsonify({"success": False, "message": "بيانات ناقصة (رقم الهاتف أو نص الرسالة مفقود)"}), 400

        success, response_data = send_text_message(phone, message)
        
        if success:
            return jsonify({"success": True, "message": "تم إرسال الرسالة بنجاح", "meta_response": response_data})
        else:
            error_msg = response_data.get('error', {}).get('message', 'خطأ غير معروف من ميتا') if isinstance(response_data, dict) else 'فشل الإرسال'
            return jsonify({"success": False, "message": error_msg}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
