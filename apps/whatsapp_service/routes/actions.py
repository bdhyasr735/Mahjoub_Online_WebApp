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
from apps.whatsapp_service.whatsapp_api import send_text_message, clean_phone_number
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog
from apps.extensions import db


# =========================================================
# 1. إرسال رسالة جديدة (HTMX)
# =========================================================
@whatsapp_bp.route('/send_message', methods=['POST'])
def send_message_htmx():
    """
    استقبال رسالة جديدة من الواجهة وإرسالها عبر ميتا وتحديث جهة الاتصال.
    """
    phone = request.form.get('phone')
    message = request.form.get('message')

    if not phone or not message:
        return "<div class='text-danger p-2'>بيانات ناقصة (الرقم أو الرسالة)</div>", 400

    cleaned_phone = clean_phone_number(phone)

    # 1. إرسال الرسالة عبر API Meta (يقوم تلقائياً بتحديث السجلات وآخر محادثة)
    success, response_data = send_text_message(cleaned_phone, message)

    if not success:
        error_msg = response_data.get('error', 'فشل إرسال الرسالة عبر Meta API')
        print(f"⚠️ [HTMX Send Error]: {error_msg}")

    # 2. إعادة تحميل قائمة جهات الاتصال المحدثة لجانب الواجهة
    return refresh_contacts()


# =========================================================
# 2. جلب منطقة الشات (HTMX)
# =========================================================
@whatsapp_bp.route('/client/<int:contact_id>/chat')
def get_chat_area(contact_id):
    """
    جلب منطقة المحادثة بالكامل لعميل معين وتصفير الرسائل غير المقروءة.
    """
    contact = db.session.query(WhatsAppCustomerContact).get(contact_id)
    if not contact:
        return "<div class='p-3 text-muted'>العميل غير موجود</div>", 404

    cleaned_phone = clean_phone_number(contact.phone)

    # تصفير عدد الرسائل غير المقروءة عند دخول المحادثة
    if contact.unread_count and contact.unread_count > 0:
        contact.unread_count = 0
        db.session.commit()

    # جلب الرسائل المطابقة للرقم الأصلي والرقم المُنظّف
    messages = db.session.query(WhatsAppMessageLog).filter(
        or_(
            WhatsAppMessageLog.sender_number == contact.phone,
            WhatsAppMessageLog.recipient_number == contact.phone,
            WhatsAppMessageLog.sender_number == cleaned_phone,
            WhatsAppMessageLog.recipient_number == cleaned_phone
        )
    ).order_by(WhatsAppMessageLog.timestamp.asc()).limit(100).all()

    return render_template('admin/components/_chat_area.html', contact=contact, messages=messages)


# =========================================================
# 3. جلب تفاصيل العميل (HTMX)
# =========================================================
@whatsapp_bp.route('/client/<int:contact_id>/details')
def get_client_details(contact_id):
    """
    جلب اللوحة الجانبية لتفاصيل العميل.
    """
    contact = db.session.query(WhatsAppCustomerContact).get(contact_id)
    if not contact:
        return "<div class='p-3 text-muted'>العميل غير موجود</div>", 404

    return render_template('admin/components/_client_details.html', contact=contact)


# =========================================================
# 4. تحديث قائمة جهات الاتصال (HTMX)
# =========================================================
@whatsapp_bp.route('/refresh_contacts')
def refresh_contacts():
    """
    تحديث قائمة جهات الاتصال في الشريط الجانبي مع احتساب حالة الاتصال الحالية.
    """
    contacts = db.session.query(WhatsAppCustomerContact).order_by(
        WhatsAppCustomerContact.last_timestamp.desc().nullslast()
    ).all()

    # تحديث حالة الاتصال المؤقتة بناءً على آخر نشاط
    for contact in contacts:
        if contact.last_timestamp:
            diff = datetime.utcnow() - contact.last_timestamp
            contact.is_online = diff < timedelta(minutes=10)
        else:
            contact.is_online = False

    return render_template('admin/components/_sidebar_contacts.html', contacts=contacts)
