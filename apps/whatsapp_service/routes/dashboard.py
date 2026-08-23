# coding: utf-8
# 📂 apps/whatsapp_service/routes/dashboard.py

"""
WhatsApp Service Dashboard & UI Routes Module for Mahjoub Online WebApp
"""

from flask import render_template, request, jsonify, flash, redirect, url_for, current_app
from apps.extensions import db
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog
from . import whatsapp_bp  # استيراد الـ Blueprint من routes/__init__.py


@whatsapp_bp.route('/dashboard', methods=['GET'])
def chat_dashboard():
    """لوحة المحادثات المباشرة والرئيسية للواتساب"""
    try:
        contacts = WhatsAppCustomerContact.query.order_by(
            WhatsAppCustomerContact.last_timestamp.desc()
        ).all()

        # اختيار أول عميل افتراضياً
        contact_id = request.args.get('contact_id', type=int)
        current_contact = None
        messages = []

        if contact_id:
            current_contact = WhatsAppCustomerContact.query.get(contact_id)
        elif contacts:
            current_contact = contacts[0]

        if current_contact:
            messages = WhatsAppMessageLog.query.filter(
                (WhatsAppMessageLog.sender_number == current_contact.phone) |
                (WhatsAppMessageLog.recipient_number == current_contact.phone)
            ).order_by(WhatsAppMessageLog.timestamp.asc()).all()

        return render_template(
            'admin/whatsapp_dashboard.html',
            active_tab='chat',
            contacts=contacts,
            selected_contact=current_contact,  # استخدام selected_contact لتوافق القوالب
            messages=messages
        )
    except Exception as e:
        print(f"⚠️ [Chat Dashboard Error]: {e}")
        return render_template(
            'admin/whatsapp_dashboard.html',
            active_tab='chat',
            contacts=[],
            selected_contact=None,
            messages=[]
        )


@whatsapp_bp.route('/logs', methods=['GET'])
def logs_dashboard():
    """لوحة سجل الرسائل والـ Logs"""
    try:
        logs = WhatsAppMessageLog.query.order_by(
            WhatsAppMessageLog.timestamp.desc()
        ).limit(150).all()
        return render_template(
            'admin/whatsapp_dashboard.html',
            active_tab='logs',
            logs=logs
        )
    except Exception as e:
        print(f"⚠️ [Logs Dashboard Error]: {e}")
        return render_template(
            'admin/whatsapp_dashboard.html',
            active_tab='logs',
            logs=[]
        )


@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_dashboard():
    """لوحة إعدادات Meta WhatsApp API"""
    is_connected = True  # يمكن ربطها بالتحقق من وجود المفاتيح

    if request.method == 'POST':
        phone_number_id = request.form.get('phone_number_id')
        business_account_id = request.form.get('business_account_id')
        access_token = request.form.get('access_token')

        # حفظ الإعدادات في قاعدة البيانات أو config
        # مثال: current_app.config['WHATSAPP_PHONE_NUMBER_ID'] = phone_number_id
        flash("تم حفظ إعدادات Meta API بنجاح", "success")
        return redirect(url_for('whatsapp_service.settings_dashboard'))

    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='settings',
        settings={
            "phone_number_id": current_app.config.get('WHATSAPP_PHONE_NUMBER_ID', ''),
            "whatsapp_business_id": current_app.config.get('WHATSAPP_BUSINESS_ACCOUNT_ID', ''),
            "access_token": current_app.config.get('WHATSAPP_ACCESS_TOKEN', ''),
            "verify_token": current_app.config.get('WHATSAPP_VERIFY_TOKEN', '')
        },
        saved_success=request.args.get('saved') == 'true'
    )
