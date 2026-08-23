# coding: utf-8
# 📂 apps/whatsapp_service/routes/actions.py

"""
HTMX Actions for WhatsApp Service
Handles dynamic UI updates: sending messages, loading chats, and refreshing contacts
"""

from flask import request, render_template
from datetime import datetime, timedelta
from sqlalchemy import or_
from . import whatsapp_bp
from apps.whatsapp_service.whatsapp_api import send_text_message
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog
from apps.extensions import db


# =========================================================
# 1. إرسال رسالة جديدة (HTMX)
# =========================================================
@whatsapp_bp.route('/send_message', methods=['POST'])
def send_message_htmx():
    """
    استقبال رسالة جديدة من الواجهة وإرسالها عبر ميتا.
    - تُحدث قاعدة البيانات.
    - تعيد تحميل قائمة جهات الاتصال لتحديث آخر رسالة.
    """
    phone = request.form.get('phone')
    message = request.form.get('message')

    if not phone or not message:
        return "بيانات ناقصة", 400

    # 1. إرسال الرسالة عبر ميتا
    success, response_data = send_text_message(phone, message)

    # 2. تحديث جهة الاتصال في قاعدة البيانات
    contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
    if contact:
        contact.last_message = message
        contact.last_timestamp = datetime.utcnow()
        db.session.commit()

    # 3. إعادة تحميل قائمة جهات الاتصال (تحديث HTMX)
    return refresh_contacts()


# =========================================================
# 2. جلب منطقة الشات (HTMX)
# =========================================================
@whatsapp_bp.route('/client/<int:contact_id>/chat')
def get_chat_area(contact_id):
    """
    جلب منطقة المحادثة بالكامل لعميل معين.
    - تُستخدم عند النقر على جهة اتصال في القائمة الجانبية.
    - تعيد مكون _chat_area.html فقط.
    """
    contact = db.session.query(WhatsAppCustomerContact).get(contact_id)
    if not contact:
        return "العميل غير موجود", 404

    # تحديث عدد الرسائل غير المقروءة إلى صفر
    if contact.unread_count and contact.unread_count > 0:
        contact.unread_count = 0
        db.session.commit()

    # جلب آخر 50 رسالة من المحادثة
    messages = db.session.query(WhatsAppMessageLog).filter(
        or_(
            WhatsAppMessageLog.sender_number == contact.phone,
            WhatsAppMessageLog.recipient_number == contact.phone
        )
    ).order_by(WhatsAppMessageLog.timestamp.asc()).limit(50).all()

    return render_template('admin/components/_chat_area.html', contact=contact, messages=messages)


# =========================================================
# 3. جلب تفاصيل العميل (HTMX)
# =========================================================
@whatsapp_bp.route('/client/<int:contact_id>/details')
def get_client_details(contact_id):
    """
    جلب تفاصيل العميل الجانبية (اللوحة اليسرى).
    - تعيد مكون _client_details.html فقط.
    """
    contact = db.session.query(WhatsAppCustomerContact).get(contact_id)
    if not contact:
        return "العميل غير موجود", 404

    return render_template('admin/components/_client_details.html', contact=contact)


# =========================================================
# 4. تحديث قائمة جهات الاتصال (HTMX)
# =========================================================
@whatsapp_bp.route('/refresh_contacts')
def refresh_contacts():
    """
    تحديث قائمة جهات الاتصال في الشريط الجانبي.
    - تُستخدم بعد إرسال رسالة أو عند تحديث البيانات.
    - تعيد مكون _sidebar_contacts.html فقط.
    """
    contacts = db.session.query(WhatsAppCustomerContact).order_by(
        WhatsAppCustomerContact.last_timestamp.desc()
    ).all()

    # تحديث حالة الاتصال (online/offline)
    for contact in contacts:
        if contact.last_timestamp:
            diff = datetime.utcnow() - contact.last_timestamp
            contact.is_online = diff < timedelta(minutes=10)
        else:
            contact.is_online = False

    return render_template('admin/components/_sidebar_contacts.html', contacts=contacts)
