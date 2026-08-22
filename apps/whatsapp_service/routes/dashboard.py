# coding: utf-8
# 📂 apps/whatsapp_service/routes/dashboard.py

import os
from datetime import datetime, timedelta
from flask import request, render_template
from sqlalchemy import or_

from apps.models.whatsapp_models import (
    WhatsAppMessageLog,
    WhatsAppCustomerContact
)
from apps.extensions import db
from . import whatsapp_bp


@whatsapp_bp.route('/dashboard')
def chat_dashboard():
    """عرض لوحة التحكم الرئيسية مع جميع جهات الاتصال وعدم فتح أي دردشة إلا عند اختيارها صراحة"""
    contacts = db.session.query(WhatsAppCustomerContact).order_by(
        WhatsAppCustomerContact.last_timestamp.desc()
    ).all()

    for contact in contacts:
        if contact.last_timestamp:
            diff = datetime.utcnow() - contact.last_timestamp
            contact.is_online = diff < timedelta(minutes=10)
        else:
            contact.is_online = False

    contact_id = request.args.get('contact_id', type=int)
    current_contact = None
    messages = []
    
    if contact_id:
        current_contact = db.session.query(WhatsAppCustomerContact).get(contact_id)
        if current_contact:
            messages = db.session.query(WhatsAppMessageLog).filter(
                or_(
                    WhatsAppMessageLog.sender_number == current_contact.phone,
                    WhatsAppMessageLog.recipient_number == current_contact.phone
                )
            ).order_by(WhatsAppMessageLog.timestamp.asc()).limit(50).all()

    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='chat',
        contacts=contacts,
        current_contact=current_contact,
        messages=messages
    )


@whatsapp_bp.route('/logs')
def logs_dashboard():
    """عرض سجل الرسائل (Logs) بالكامل"""
    logs = db.session.query(WhatsAppMessageLog).order_by(WhatsAppMessageLog.timestamp.desc()).all()
    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='logs',
        logs=logs
    )


@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_dashboard():
    """إعدادات ربط واتساب وتحديث مفاتيح Meta API"""
    if request.method == 'POST':
        # يمكنك إضافة منطق حفظ المفاتيح هنا حسب الحاجة
        pass
        
    is_connected = bool(os.getenv('WHATSAPP_ACCESS_TOKEN') or os.getenv('WHATSAPP_PHONE_NUMBER_ID'))
    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='settings',
        is_connected=is_connected
    )


@whatsapp_bp.route('/partials/contacts', methods=['GET'])
def partials_contacts():
    """جلب قائمة جهات الاتصال جزئياً لتحديثها عبر HTMX"""
    contacts = db.session.query(WhatsAppCustomerContact).order_by(
        WhatsAppCustomerContact.last_timestamp.desc()
    ).all()

    for contact in contacts:
        if contact.last_timestamp:
            diff = datetime.utcnow() - contact.last_timestamp
            contact.is_online = diff < timedelta(minutes=10)
        else:
            contact.is_online = False

    current_contact_id = request.args.get('contact_id', type=int)
    
    return render_template(
        'admin/partials/contacts_list.html',
        contacts=contacts,
        current_contact_id=current_contact_id
    )


@whatsapp_bp.route('/partials/chat-window', methods=['GET'])
def partials_chat_window():
    """جلب نافذة المحادثة والرسائل لعميل محدد عبر الـ contact_id"""
    contact_id = request.args.get('contact_id', type=int)
    if not contact_id:
        return '<div class="flex items-center justify-center h-full text-slate-400">اختر عميلاً لعرض المحادثة</div>', 400

    current_contact = db.session.query(WhatsAppCustomerContact).get_or_404(contact_id)
    
    if current_contact.unread_count > 0:
        current_contact.unread_count = 0
        db.session.commit()

    messages = db.session.query(WhatsAppMessageLog).filter(
        or_(
            WhatsAppMessageLog.sender_number == current_contact.phone,
            WhatsAppMessageLog.recipient_number == current_contact.phone
        )
    ).order_by(WhatsAppMessageLog.timestamp.asc()).all()

    return render_template(
        'admin/partials/chat_window.html',
        current_contact=current_contact,
        messages=messages
    )


@whatsapp_bp.route('/partials/client-details', methods=['GET'])
def partials_client_details():
    """جلب تفاصيل العميل الجانبية (اللوحة اليسرى)"""
    contact_id = request.args.get('contact_id', type=int)
    if not contact_id:
        return '<div class="p-4 text-slate-400 text-center">لا توجد بيانات محددة</div>', 400

    current_contact = db.session.query(WhatsAppCustomerContact).get_or_404(contact_id)
    
    return render_template(
        'admin/partials/client_sidebar.html',
        current_contact=current_contact
    )
