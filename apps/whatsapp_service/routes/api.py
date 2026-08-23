# coding: utf-8
# 📂 apps/whatsapp_service/routes/api.py

"""
RESTful API Endpoints for WhatsApp Service
Provides JSON responses for external integrations and JavaScript fetch calls
"""

from flask import request, jsonify
from sqlalchemy import or_
from . import whatsapp_bp
from apps.whatsapp_service.whatsapp_api import send_text_message
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog
from apps.extensions import db


# =========================================================
# 1. جلب محادثة عميل معين (JSON)
# =========================================================
@whatsapp_bp.route('/api/whatsapp/conversation/<phone>', methods=['GET'])
def get_conversation_data(phone):
    """
    جلب جميع رسائل عميل معين بصيغة JSON.
    - تُستخدم من قبل JavaScript لتحديث الشات يدوياً.
    """
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


# =========================================================
# 2. إرسال رسالة عبر JSON (API)
# =========================================================
@whatsapp_bp.route('/api/whatsapp/send', methods=['POST'])
def send_message_api():
    """
    إرسال رسالة عبر JSON (للاستخدام مع التطبيقات الخارجية).
    - تُستخدم من قبل Postman أو تطبيقات أخرى.
    """
    data = request.get_json(silent=True) or {}
    phone = data.get('phone')
    message = data.get('message')
    order_id = data.get('order_id')

    if not phone or not message:
        return jsonify({"success": False, "error": "بيانات ناقصة"}), 400

    success, response_data = send_text_message(phone, message)

    # تسجيل الرسالة في قاعدة البيانات إذا نجحت
    if success:
        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
        if contact:
            contact.last_message = message
            contact.last_timestamp = datetime.utcnow()
            db.session.commit()

    return jsonify({
        "success": success,
        "meta_response": response_data,
        "message": "تم الإرسال بنجاح" if success else "فشل الإرسال"
    }), 200 if success else 500


# =========================================================
# 3. اختبار صحة الاتصال (Ping)
# =========================================================
@whatsapp_bp.route('/api/whatsapp/ping', methods=['GET'])
def ping_api():
    """
    اختبار صحة الخدمة.
    - تُستخدم لمراقبة الخادم (Health Check).
    """
    return jsonify({
        "status": "active",
        "service": "WhatsApp Service",
        "version": "1.2.0",
        "timestamp": datetime.utcnow().isoformat()
    })
