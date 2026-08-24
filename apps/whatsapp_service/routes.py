# coding: utf-8

import os
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, flash
from apps.extensions import db, csrf
from apps.models.whatsapp_models import (
    WhatsAppCustomerContact, 
    WhatsAppMessageLog, 
    WhatsAppSettings
)
from apps.whatsapp_service.whatsapp_api import send_text_message
from apps.whatsapp_service.config import WhatsAppServiceConfig

# ✅ تعريف الـ Blueprint بالاسم المطلوب في القوالب
whatsapp_bp = Blueprint('whatsapp_service', __name__, template_folder='templates')


# ============================================================
# ✅ Context Processor لتوفير الإعدادات لجميع القوالب تلقائياً
# ============================================================
@whatsapp_bp.context_processor
def inject_settings():
    """حقن متغير settings في جميع قوالب الـ Blueprint"""
    settings = {
        'phone_number_id': WhatsAppSettings.get_setting('WHATSAPP_PHONE_NUMBER_ID') or WhatsAppServiceConfig.get_phone_number_id(),
        'business_account_id': WhatsAppSettings.get_setting('WHATSAPP_BUSINESS_ACCOUNT_ID') or WhatsAppServiceConfig.get_business_account_id(),
        'api_version': WhatsAppSettings.get_setting('WHATSAPP_API_VERSION') or WhatsAppServiceConfig.get_api_version(),
        'access_token': WhatsAppSettings.get_setting('WHATSAPP_TOKEN') or WhatsAppServiceConfig.get_whatsapp_token(),
        'verify_token': WhatsAppSettings.get_setting('WHATSAPP_VERIFY_TOKEN') or WhatsAppServiceConfig.get_verify_token(),
        'webhook_secret': WhatsAppSettings.get_setting('WEBHOOK_SECRET') or WhatsAppServiceConfig.get_webhook_secret(),
    }
    return {'settings': settings}


# ============================================================
# المسارات (Routes)
# ============================================================

@whatsapp_bp.route('/chat')
def chat_dashboard():
    """عرض لوحة المحادثات مع قائمة جهات الاتصال والرسائل"""
    contacts = WhatsAppCustomerContact.query.order_by(
        WhatsAppCustomerContact.last_timestamp.desc()
    ).all()
    
    contact_id = request.args.get('contact_id', type=int)
    selected_phone = request.args.get('phone')
    
    messages = []
    active_contact = None

    if contact_id:
        active_contact = WhatsAppCustomerContact.query.get(contact_id)
        if active_contact:
            selected_phone = active_contact.phone
    elif selected_phone:
        active_contact = WhatsAppCustomerContact.query.filter_by(phone=selected_phone).first()
    elif contacts:
        active_contact = contacts[0]
        selected_phone = active_contact.phone

    if active_contact and selected_phone:
        if active_contact.unread_count and active_contact.unread_count > 0:
            active_contact.unread_count = 0
            db.session.commit()
        
        messages = WhatsAppMessageLog.query.filter(
            (WhatsAppMessageLog.sender_number == selected_phone) |
            (WhatsAppMessageLog.recipient_number == selected_phone)
        ).order_by(WhatsAppMessageLog.timestamp.asc()).all()

    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='chat',
        contacts=contacts,
        selected_contact=active_contact,
        messages=messages,
        selected_phone=selected_phone
    )


@whatsapp_bp.route('/send-message', methods=['POST'])
@csrf.exempt
def send_message_htmx():
    """إرسال رسالة عبر واتساب مع دعم HTMX"""
    recipient = request.form.get('recipient') or request.json.get('recipient')
    if not recipient:
        recipient = request.form.get('phone')
    
    message = request.form.get('message') or request.json.get('message')

    if not recipient or not message:
        return jsonify({"success": False, "error": "المستلم أو نص الرسالة غير موجود."}), 400

    success, result = send_text_message(recipient, message)
    
    if success:
        if request.headers.get('HX-Request'):
            new_msg = WhatsAppMessageLog.query.filter_by(
                recipient_number=recipient
            ).order_by(WhatsAppMessageLog.id.desc()).first()
            return render_template('whatsapp/_message_bubble.html', msg=new_msg)
        return jsonify({"success": True, "result": result})
    else:
        return jsonify({"success": False, "error": str(result)}), 500


@whatsapp_bp.route('/start-new-chat', methods=['POST'])
@csrf.exempt
def start_new_chat():
    """بدء محادثة جديدة مع عميل"""
    phone = request.form.get('phone')
    name = request.form.get('name', f"عميل ({phone})")

    if not phone:
        flash('رقم الهاتف مطلوب لبدء المحادثة', 'error')
        return redirect(url_for('whatsapp_service.chat_dashboard'))

    contact = WhatsAppCustomerContact.query.filter_by(phone=phone).first()
    if not contact:
        contact = WhatsAppCustomerContact(
            phone=phone,
            name=name,
            last_message="",
            last_timestamp=datetime.now(timezone.utc),
            unread_count=0
        )
        db.session.add(contact)
        db.session.commit()
    else:
        if name and name != contact.name:
            contact.name = name
            db.session.commit()

    return redirect(url_for('whatsapp_service.chat_dashboard', phone=phone))


@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_view():
    """صفحة إعدادات واتساب (عرض وحفظ)"""
    if request.method == 'POST':
        phone_id = request.form.get('whatsapp_phone_number_id')
        token = request.form.get('whatsapp_token')
        verify_token = request.form.get('whatsapp_verify_token')
        api_version = request.form.get('whatsapp_api_version', 'v21.0')

        WhatsAppSettings.set_setting('WHATSAPP_PHONE_NUMBER_ID', phone_id)
        WhatsAppSettings.set_setting('WHATSAPP_TOKEN', token)
        WhatsAppSettings.set_setting('WHATSAPP_VERIFY_TOKEN', verify_token)
        WhatsAppSettings.set_setting('WHATSAPP_API_VERSION', api_version)

        flash('تم حفظ الإعدادات بنجاح', 'success')
        return redirect(url_for('whatsapp_service.settings_view'))

    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='settings'
    )


@whatsapp_bp.route('/logs')
def logs_dashboard():
    """صفحة سجل الرسائل"""
    logs = WhatsAppMessageLog.query.order_by(WhatsAppMessageLog.timestamp.desc()).all()
    
    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='logs',
        logs=logs
    )


@whatsapp_bp.route('/webhook-dashboard')
def webhook_dashboard():
    """صفحة محاكي الـ Webhook (للعرض فقط)"""
    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='webhook'
    )


# ============================================================
# 🚨 المسار الرئيسي لـ Webhook (يجب أن يكون متطابقاً مع ما في ميتا)
# ============================================================
@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
@csrf.exempt
def webhook_handler():
    """
    نقطة استقبال Webhook من ميتا (GET للتحقق، POST للاستقبال)
    هذا هو المسار الذي يجب إضافته في لوحة تحكم ميتا
    """
    if request.method == 'GET':
        # التحقق من التوكن
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        verify_token = WhatsAppServiceConfig.get_verify_token()
        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                return challenge, 200
            else:
                return 'Verification token mismatch', 403
        return 'Hello WhatsApp Webhook', 200

    elif request.method == 'POST':
        # ✅ التحقق من وجود بيانات JSON صالحة
        if not request.is_json:
            current_app.logger.warning("Webhook POST: No JSON data received")
            return jsonify({"status": "error", "message": "Expected JSON"}), 400

        data = request.json
        if not data:
            current_app.logger.warning("Webhook POST: Empty JSON data")
            return jsonify({"status": "error", "message": "Empty data"}), 400

        try:
            entries = data.get('entry', [])
            if not entries:
                current_app.logger.info("Webhook POST: No entries in data")
                return jsonify({"status": "success", "message": "No entries"}), 200

            for entry in entries:
                changes = entry.get('changes', [])
                for change in changes:
                    value = change.get('value', {})
                    
                    # معالجة الرسائل الواردة
                    messages = value.get('messages', [])
                    for msg in messages:
                        sender = msg.get('from')
                        msg_body = msg.get('text', {}).get('body', '')
                        wamid = msg.get('id')
                        msg_type = msg.get('type', 'text')

                        log_entry = WhatsAppMessageLog(
                            wamid=wamid,
                            direction='inbound',
                            sender_number=sender,
                            recipient_number=WhatsAppServiceConfig.get_phone_number_id(),
                            content=msg_body,
                            message_type=msg_type,
                            status='received'
                        )
                        db.session.add(log_entry)

                        contact = WhatsAppCustomerContact.query.filter_by(phone=sender).first()
                        if contact:
                            contact.last_message = msg_body
                            contact.last_timestamp = datetime.now(timezone.utc)
                            contact.unread_count = (contact.unread_count or 0) + 1
                        else:
                            new_contact = WhatsAppCustomerContact(
                                phone=sender,
                                name=f"عميل ({sender})",
                                last_message=msg_body,
                                last_timestamp=datetime.now(timezone.utc),
                                unread_count=1
                            )
                            db.session.add(new_contact)
                        
                        db.session.commit()

                    # معالجة تحديثات حالة الرسائل
                    statuses = value.get('statuses', [])
                    for st in statuses:
                        wamid = st.get('id')
                        status_type = st.get('status')
                        msg_log = WhatsAppMessageLog.query.filter_by(wamid=wamid).first()
                        if msg_log:
                            msg_log.status = status_type
                            db.session.commit()

        except Exception as e:
            current_app.logger.error(f"Webhook error: {str(e)}")
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

        return jsonify({"status": "success"}), 200


# ============================================================
# نسخة احتياطية (للتوافق مع الإعدادات القديمة في ميتا)
# ============================================================
@whatsapp_bp.route('/webhook-handler', methods=['GET', 'POST'])
@csrf.exempt
def whatsapp_webhook_handler():
    """نسخة احتياطية من Webhook (تُعيد توجيه الطلب إلى المعالج الرئيسي)"""
    return webhook_handler()


@whatsapp_bp.route('/settings/save', methods=['POST'])
@csrf.exempt
def settings_save():
    """نقطة API لحفظ الإعدادات عبر AJAX (تستخدم في settings_view.html)"""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        phone_number_id = data.get('phone_number_id')
        business_account_id = data.get('business_account_id')
        api_version = data.get('api_version')
        access_token = data.get('access_token')

        if phone_number_id:
            WhatsAppSettings.set_setting('WHATSAPP_PHONE_NUMBER_ID', phone_number_id)
        if business_account_id:
            WhatsAppSettings.set_setting('WHATSAPP_BUSINESS_ACCOUNT_ID', business_account_id)
        if api_version:
            WhatsAppSettings.set_setting('WHATSAPP_API_VERSION', api_version)
        if access_token:
            WhatsAppSettings.set_setting('WHATSAPP_TOKEN', access_token)

        return jsonify({"success": True, "message": "تم حفظ الإعدادات بنجاح"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
