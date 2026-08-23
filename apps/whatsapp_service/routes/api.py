# coding: utf-8
# 📂 apps/whatsapp_service/routes/api.py

"""
RESTful API Endpoints for WhatsApp Service
Provides JSON responses for internal UI components, JavaScript AJAX calls,
and external system integrations.
"""

from datetime import datetime
from flask import request, jsonify
from sqlalchemy import or_
from . import whatsapp_bp
from apps.whatsapp_service.whatsapp_api import (
    send_text_message,
    send_template_message,
    send_media_message,
    clean_phone_number
)
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog
from apps.extensions import db, csrf


# =========================================================
# 1. جلب محادثة عميل معين (JSON)
# =========================================================
@whatsapp_bp.route('/api/whatsapp/conversation/<phone>', methods=['GET'])
def get_conversation_data(phone):
    """
    جلب جميع رسائل عميل معين بصيغة JSON لتحديث واجهة الشات ديناميكياً (AJAX).
    """
    cleaned_phone = clean_phone_number(phone)

    # البحث عن جهة الاتصال برقم العميل الأصلي والمُنظّف
    contact = db.session.query(WhatsAppCustomerContact).filter(
        or_(
            WhatsAppCustomerContact.phone == phone,
            WhatsAppCustomerContact.phone == cleaned_phone
        )
    ).first()

    if contact and (contact.unread_count or 0) > 0:
        contact.unread_count = 0
        db.session.commit()

    # جلب الرسائل بناءً على الرقم المُنظّف والرقم الأصلي
    messages = db.session.query(WhatsAppMessageLog).filter(
        or_(
            WhatsAppMessageLog.sender_number == phone,
            WhatsAppMessageLog.recipient_number == phone,
            WhatsAppMessageLog.sender_number == cleaned_phone,
            WhatsAppMessageLog.recipient_number == cleaned_phone
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
        "name": contact.name if contact else f"عميل ({phone})",
        "phone": phone,
        "whatsapp_profile_name": getattr(contact, 'whatsapp_profile_name', None) if contact else None
    }

    return jsonify({
        "success": True,
        "client": client_info,
        "messages": messages_data
    })


# =========================================================
# 2. إرسال رسالة نصية أو قالب عبر REST API (JSON)
# =========================================================
@whatsapp_bp.route('/api/whatsapp/send', methods=['POST'])
@csrf.exempt  # تمكين استدعاء الـ API من الأنظمة الخارجية والبرمجيات دون تعارض CSRF
def send_message_api():
    """
    إرسال رسالة نصية أو قالب مخصص أو وسائط عبر JSON.
    """
    data = request.get_json(silent=True) or {}
    phone = data.get('phone')
    msg_type = data.get('type', 'text')  # 'text' أو 'template' أو 'media'
    message = data.get('message')

    # بيانات القوالب والوسائط إن وجدت
    template_name = data.get('template_name')
    language_code = data.get('language_code', 'ar')
    components = data.get('components', [])
    media_url = data.get('media_url')

    if not phone:
        return jsonify({"success": False, "error": "رقم الهاتف مطلوب"}), 400

    cleaned_phone = clean_phone_number(phone)

    # 1. إرسال قالب معتمد من Meta
    if msg_type == 'template' and template_name:
        success, response_data = send_template_message(
            recipient=cleaned_phone,
            template_name=template_name,
            language_code=language_code,
            components=components
        )
    # 2. إرسال وسائط (صورة/فيديو/مستند)
    elif msg_type == 'media' and media_url:
        media_kind = data.get('media_type', 'image')
        success, response_data = send_media_message(
            recipient=cleaned_phone,
            media_url=media_url,
            media_type=media_kind,
            caption=message
        )
    # 3. إرسال رسالة نصية اعتيادية
    else:
        if not message:
            return jsonify({"success": False, "error": "نص الرسالة مطلوب"}), 400
        success, response_data = send_text_message(cleaned_phone, message)

    return jsonify({
        "success": success,
        "meta_response": response_data,
        "message": "تم الإرسال بنجاح" if success else "فشل الإرسال"
    }), 200 if success else 500


# =========================================================
# 3. اختبار صحة الاتصال (Ping & Health Check)
# =========================================================
@whatsapp_bp.route('/api/whatsapp/ping', methods=['GET'])
def ping_api():
    """اختبار صحة خدمة الواتساب ومراقبة التشغيل"""
    return jsonify({
        "status": "active",
        "service": "Mahjoub Online WhatsApp API",
        "version": "1.2.0",
        "timestamp": datetime.utcnow().isoformat()
    })
