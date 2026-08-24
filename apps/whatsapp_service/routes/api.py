# coding: utf-8
"""
WhatsApp JSON APIs
Handles real-time polling data retrieval and AJAX live message sending.
"""

from flask import request, jsonify
from sqlalchemy import or_
from datetime import datetime
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
    """إرسال رسالة مباشرة وفورية عبر AJAX JSON مع حفظها في السجلات"""
    try:
        data = request.get_json(silent=True) or {}
        phone = data.get('phone')
        message = data.get('message')
        
        if not phone or not message:
            return jsonify({"success": False, "message": "بيانات ناقصة (رقم الهاتف أو نص الرسالة مفقود)"}), 400

        # إرسال الرسالة عبر خدمة Meta WhatsApp API
        success, response_data = send_text_message(phone, message)
        
        if success:
            # استخراج wamid الخاص بالرسالة الصادرة من استجابة ميتا إن وجد
            wamid = None
            if isinstance(response_data, dict):
                messages_meta = response_data.get('messages', [])
                if messages_meta:
                    wamid = messages_meta[0].get('id')

            now_time = datetime.utcnow()

            # حفظ الرسالة الصادرة في جدول سجلات الرسائل
            new_log = WhatsAppMessageLog(
                wamid=wamid,
                direction='outbound',
                sender_number='system', # أو رقم هاتف النشاط التجاري الخاص بك
                recipient_number=phone,
                content=message,
                status='sent',
                timestamp=now_time
            )
            db.session.add(new_log)

            # تحديث آخر رسالة وتوقيتها في جدول جهات الاتصال للعميل
            contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
            if contact:
                contact.last_message = message
                contact.last_timestamp = now_time
            else:
                # إذا لم يكن العميل موجوداً مسبقاً، يتم إضافته
                new_contact = WhatsAppCustomerContact(
                    phone=phone,
                    name=f"عميل ({phone})",
                    last_message=message,
                    last_timestamp=now_time,
                    unread_count=0
                )
                db.session.add(new_contact)

            db.session.commit()

            return jsonify({
                "success": True, 
                "message": "تم إرسال الرسالة وحفظها بنجاح", 
                "meta_response": response_data
            })
        else:
            error_msg = response_data.get('error', {}).get('message', 'خطأ غير معروف من ميتا') if isinstance(response_data, dict) else 'فشل الإرسال'
            return jsonify({"success": False, "message": error_msg}), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
