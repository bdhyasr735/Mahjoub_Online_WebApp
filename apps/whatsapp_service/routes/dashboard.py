# coding: utf-8
# 📂 apps/whatsapp_service/routes/dashboard.py

"""
WhatsApp Admin Dashboard Routes
Renders the chat interface, logs table, settings view, and health check.
"""

from datetime import datetime, timedelta
from flask import render_template, request, jsonify, redirect, url_for
from sqlalchemy import or_
from . import whatsapp_bp
from apps.whatsapp_service.config import WhatsAppServiceConfig
from apps.models.whatsapp_models import (
    WhatsAppMessageLog,
    WhatsAppCustomerContact
)
from apps.extensions import db


@whatsapp_bp.route('/dashboard')
def chat_dashboard():
    """عرض لوحة التحكم الرئيسية مع جميع جهات الاتصال وأول عميل محدد"""
    contacts = db.session.query(WhatsAppCustomerContact).order_by(
        WhatsAppCustomerContact.last_timestamp.desc()
    ).all()

    # تعيين حالة الاتصال (online/offline)
    for contact in contacts:
        if contact.last_timestamp:
            diff = datetime.utcnow() - contact.last_timestamp
            contact.is_online = diff < timedelta(minutes=10)
        else:
            contact.is_online = False

    # قراءة رقم العميل المحدد من الرابط (مثل ?contact_id=1)
    contact_id = request.args.get('contact_id', type=int)
    
    current_contact = None
    if contact_id:
        current_contact = db.session.query(WhatsAppCustomerContact).get(contact_id)
    
    if not current_contact and contacts:
        current_contact = contacts[0]
    
    # تصفير عدد غير المقروء عند فتح المحادثة
    if current_contact and current_contact.unread_count > 0:
        current_contact.unread_count = 0
        db.session.commit()

    messages = []
    if current_contact:
        messages = db.session.query(WhatsAppMessageLog).filter(
            or_(
                WhatsAppMessageLog.sender_number == current_contact.phone,
                WhatsAppMessageLog.recipient_number == current_contact.phone
            )
        ).order_by(WhatsAppMessageLog.timestamp.asc()).limit(100).all()

    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='chat',
        contacts=contacts,
        current_contact=current_contact,
        messages=messages
    )


@whatsapp_bp.route('/logs')
def logs_dashboard():
    """عرض سجل الرسائل"""
    logs = db.session.query(WhatsAppMessageLog).order_by(WhatsAppMessageLog.id.desc()).limit(150).all()
    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='logs',
        logs=logs
    )


@whatsapp_bp.route('/settings')
def settings_dashboard():
    """عرض شاشة إعدادات الربط مع Meta مع تمرير كائن settings المتوافق مع القالب"""
    phone_id = WhatsAppServiceConfig.get_phone_number_id()
    access_token = WhatsAppServiceConfig.get_whatsapp_token()
    is_connected = bool(phone_id and access_token)

    # هيكل بيانات settings المتوافق مع متغيرات template (settings_view.html)
    settings_data = {
        "phone_number_id": phone_id,
        "business_account_id": WhatsAppServiceConfig.get_business_account_id(),
        "whatsapp_phone_number": WhatsAppServiceConfig.get_twilio_number(),
        "access_token": access_token,
        "verify_token": WhatsAppServiceConfig.get_verify_token(),
        "api_version": WhatsAppServiceConfig.get_api_version(),
        "updated_at": None  # يمكن استبداله بتاريخ التحديث الفعلي من قاعدة البيانات إن وجد
    }

    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='settings',
        settings=settings_data,
        is_connected=is_connected
    )


@whatsapp_bp.route('/webhook-simulator')
def webhook_dashboard():
    """محاكي الويب هوك لتفادي خطأ BuildError في القالب"""
    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='webhook'
    )


@whatsapp_bp.route('/chat/new', methods=['POST'])
def start_new_chat():
    """بدء محادثة جديدة أو حفظ رقم جديد"""
    phone = request.form.get('phone')
    name = request.form.get('name')
    
    if phone:
        existing = WhatsAppCustomerContact.query.filter_by(phone=phone).first()
        if not existing:
            new_contact = WhatsAppCustomerContact(phone=phone, name=name)
            db.session.add(new_contact)
            db.session.commit()
            return redirect(url_for('whatsapp_service.chat_dashboard', contact_id=new_contact.id))
        else:
            return redirect(url_for('whatsapp_service.chat_dashboard', contact_id=existing.id))
            
    return redirect(url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/chat/send', methods=['POST'])
def send_message():
    """إرسال رسالة جديدة من لوحة التحكم"""
    phone = request.form.get('phone')
    content = request.form.get('content')
    
    if phone and content:
        new_log = WhatsAppMessageLog(
            direction='outbound',
            sender_number='system',
            recipient_number=phone,
            content=content,
            message_type='text',
            status='sent'
        )
        db.session.add(new_log)
        db.session.commit()
        
    return redirect(request.referrer or url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/ping')
def ping():
    """فحص حالة الخدمة"""
    return jsonify({
        "status": "active",
        "service": "WhatsApp Service",
        "version": "1.2.0"
    })
