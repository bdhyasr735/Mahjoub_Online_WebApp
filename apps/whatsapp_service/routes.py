# coding: utf-8

import os
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, flash
from apps.extensions import db, csrf
from apps.models.whatsapp_models import (
    WhatsAppCustomerContact, 
    WhatsAppMessageLog, 
    WhatsAppSettings
)
from apps.whatsapp_service.whatsapp_api import send_text_message
from apps.whatsapp_service.config import WhatsAppServiceConfig

# ✅ تعريف الـ Blueprint
whatsapp_bp = Blueprint('whatsapp_service', __name__, template_folder='templates')

# ✅ استثناء البلوبرنت من CSRF
csrf.exempt(whatsapp_bp)


# ============================================================
# Context Processor لتوفير الإعدادات (محمي ضد الأخطاء)
# ============================================================
@whatsapp_bp.context_processor
def inject_settings():
    try:
        settings = {
            'phone_number_id': WhatsAppSettings.get_setting('WHATSAPP_PHONE_NUMBER_ID') or WhatsAppServiceConfig.get_phone_number_id(),
            'business_account_id': WhatsAppSettings.get_setting('WHATSAPP_BUSINESS_ACCOUNT_ID') or WhatsAppServiceConfig.get_business_account_id(),
            'api_version': WhatsAppSettings.get_setting('WHATSAPP_API_VERSION') or WhatsAppServiceConfig.get_api_version(),
            'access_token': WhatsAppSettings.get_setting('WHATSAPP_TOKEN') or WhatsAppServiceConfig.get_whatsapp_token(),
            'verify_token': WhatsAppSettings.get_setting('WHATSAPP_VERIFY_TOKEN') or WhatsAppServiceConfig.get_verify_token(),
            'webhook_secret': WhatsAppSettings.get_setting('WEBHOOK_SECRET') or WhatsAppServiceConfig.get_webhook_secret(),
        }
    except Exception as e:
        current_app.logger.error(f"Error loading settings: {e}")
        settings = {
            'phone_number_id': None,
            'business_account_id': None,
            'api_version': 'v21.0',
            'access_token': None,
            'verify_token': None,
            'webhook_secret': None,
        }
    return {'settings': settings}


# ============================================================
# المسارات
# ============================================================

@whatsapp_bp.route('/chat')
def chat_dashboard():
    try:
        contacts = WhatsAppCustomerContact.query.order_by(
            WhatsAppCustomerContact.last_timestamp.desc()
        ).all()
        
        # ✅ حساب عدد المحادثات غير المقروءة للعداد في الشريط الجانبي
        unread_chats = sum(c.unread_count or 0 for c in contacts)

    except Exception:
        contacts = []
        unread_chats = 0
    
    contact_id = request.args.get('contact_id', type=int)
    selected_phone = request.args.get('phone')
    
    if selected_phone:
        selected_phone = ''.join(filter(str.isdigit, selected_phone))
    
    messages = []
    active_contact = None

    try:
        if contact_id:
            active_contact = WhatsAppCustomerContact.query.get(contact_id)
            if active_contact:
                selected_phone = ''.join(filter(str.isdigit, active_contact.phone))
        elif selected_phone:
            active_contact = WhatsAppCustomerContact.query.filter_by(phone=selected_phone).first()
        elif contacts:
            active_contact = contacts[0]
            selected_phone = ''.join(filter(str.isdigit, active_contact.phone))

        if active_contact and selected_phone:
            if active_contact.unread_count and active_contact.unread_count > 0:
                active_contact.unread_count = 0
                db.session.commit()
            
            messages = WhatsAppMessageLog.query.filter(
                (WhatsAppMessageLog.sender_number == selected_phone) |
                (WhatsAppMessageLog.recipient_number == selected_phone)
            ).order_by(WhatsAppMessageLog.timestamp.asc()).all()
    except Exception:
        db.session.rollback()

    now = datetime.now(timezone.utc)
    today = now.strftime('%Y-%m-%d')
    yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')

    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='chat',
        contacts=contacts,
        selected_contact=active_contact,
        messages=messages,
        selected_phone=selected_phone,
        now=now,
        today=today,
        yesterday=yesterday,
        unread_chats=unread_chats  # ✅ تمرير العداد
    )


@whatsapp_bp.route('/send-message', methods=['POST'])
def send_message_htmx():
    recipient = request.form.get('phone') or request.form.get('recipient')
    message = request.form.get('message')

    if not recipient or not message:
        return jsonify({"success": False, "error": "المستلم أو نص الرسالة غير موجود."}), 400

    success, result = send_text_message(recipient, message)
    
    if success:
        # حفظ الرسالة محلياً في السجل كرسالة صادرة لضمان ظهورها الفوري
        try:
            outbound_log = WhatsAppMessageLog(
                wamid=result.get('messages', [{}])[0].get('id', 'local_sent'),
                direction='outbound',
                sender_number=WhatsAppServiceConfig.get_phone_number_id(),
                recipient_number=recipient,
                content=message,
                message_type='text',
                status='sent'
            )
            db.session.add(outbound_log)
            
            # تحديث آخر رسالة وجهة اتصال
            contact = WhatsAppCustomerContact.query.filter_by(phone=recipient).first()
            if contact:
                contact.last_message = message
                contact.last_timestamp = datetime.now(timezone.utc)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Error saving outbound message: {e}")
            db.session.rollback()

        if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return f"""
            <div class="flex justify-end animate-fadeIn">
                <div class="max-w-[75%] bg-[#570575] border royal-border rounded-2xl px-4 py-2.5 shadow-md text-xs text-white relative">
                    <p class="whitespace-pre-wrap leading-relaxed pb-3">{message}</p>
                    <div class="absolute bottom-1.5 left-3 flex items-center gap-1">
                        <span class="text-[9px] text-purple-200">الآن</span>
                        <span class="text-[10px] font-bold text-[#D4AF37]">✓</span>
                    </div>
                </div>
            </div>
            """
        return jsonify({"success": True, "result": result})
    else:
        if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return f"""
            <div class="flex justify-start animate-fadeIn">
                <div class="max-w-[75%] bg-red-950/40 border border-red-500/30 rounded-2xl px-4 py-2.5 shadow-md text-xs text-red-300">
                    <p class="whitespace-pre-wrap leading-relaxed">❌ فشل الإرسال: {str(result)[:100]}</p>
                </div>
            </div>
            """
        return jsonify({"success": False, "error": str(result)}), 500


@whatsapp_bp.route('/start-new-chat', methods=['POST'])
def start_new_chat():
    phone = request.form.get('phone')
    if not phone:
        if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "error": "رقم الهاتف مطلوب"}), 400
        flash('رقم الهاتف مطلوب لبدء المحادثة', 'error')
        return redirect(url_for('whatsapp_service.chat_dashboard'))
    
    phone = ''.join(filter(str.isdigit, phone))
    name = request.form.get('name', f"عميل ({phone})")

    try:
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
    except Exception:
        db.session.rollback()

    if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"success": True, "phone": phone, "name": contact.name})

    return redirect(url_for('whatsapp_service.chat_dashboard', phone=phone))


# ✅ دالة لعرض الإعدادات وحفظها (GET و POST)
@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_view():
    if request.method == 'POST':
        try:
            phone_id = request.form.get('whatsapp_phone_number_id')
            business_account_id = request.form.get('whatsapp_business_account_id')
            token = request.form.get('whatsapp_token')
            verify_token = request.form.get('whatsapp_verify_token')
            api_version = request.form.get('whatsapp_api_version', 'v21.0')

            WhatsAppSettings.set_setting('WHATSAPP_PHONE_NUMBER_ID', phone_id)
            WhatsAppSettings.set_setting('WHATSAPP_BUSINESS_ACCOUNT_ID', business_account_id)
            WhatsAppSettings.set_setting('WHATSAPP_TOKEN', token)
            WhatsAppSettings.set_setting('WHATSAPP_VERIFY_TOKEN', verify_token)
            WhatsAppSettings.set_setting('WHATSAPP_API_VERSION', api_version)

            flash('تم حفظ الإعدادات بنجاح', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء الحفظ: {str(e)}', 'error')

        return redirect(url_for('whatsapp_service.settings_view'))

    settings_data = inject_settings()['settings']
    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='settings',
        settings=settings_data
    )


# ✅ دالة بديلة لحفظ الإعدادات عبر JSON
@whatsapp_bp.route('/save-settings', methods=['POST'])
def save_settings():
    try:
        data = request.form if request.form else request.json
        if not data:
            return jsonify({"success": False, "message": "No data"}), 400

        phone_number_id = data.get('phone_number_id') or data.get('whatsapp_phone_number_id')
        business_account_id = data.get('business_account_id') or data.get('whatsapp_business_account_id')
        api_version = data.get('api_version') or data.get('whatsapp_api_version')
        access_token = data.get('access_token') or data.get('whatsapp_token')

        if phone_number_id:
            WhatsAppSettings.set_setting('WHATSAPP_PHONE_NUMBER_ID', phone_number_id)
        if business_account_id:
            WhatsAppSettings.set_setting('WHATSAPP_BUSINESS_ACCOUNT_ID', business_account_id)
        if api_version:
            WhatsAppSettings.set_setting('WHATSAPP_API_VERSION', api_version)
        if access_token:
            WhatsAppSettings.set_setting('WHATSAPP_TOKEN', access_token)

        return jsonify({"success": True, "message": "تم حفظ الإعدادات"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ✅ دالة السجل (محدثة لتمرير الإحصائيات)
@whatsapp_bp.route('/logs')
def logs_dashboard():
    try:
        logs = WhatsAppMessageLog.query.order_by(WhatsAppMessageLog.timestamp.desc()).all()
        
        total_logs = len(logs)
        inbound_logs = sum(1 for log in logs if log.direction == 'inbound')
        outbound_logs = sum(1 for log in logs if log.direction == 'outbound')
        unread_logs = sum(1 for log in logs if log.status == 'received' or log.status == 'sent')
        
    except Exception:
        logs = []
        total_logs = inbound_logs = outbound_logs = unread_logs = 0
        
    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='logs',
        logs=logs,
        total_logs=total_logs,
        inbound_logs=inbound_logs,
        outbound_logs=outbound_logs,
        unread_logs=unread_logs
    )


@whatsapp_bp.route('/webhook-dashboard')
def webhook_dashboard():
    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='webhook'
    )


# ============================================================
# Webhook الرئيسي (محدث لاستقبال جميع أنواع الرسائل)
# ============================================================
@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
def webhook_handler():
    if request.method == 'GET':
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
        current_app.logger.info(f"Webhook Payload Received: {request.get_data(as_text=True)}")

        if not request.is_json:
            return jsonify({"status": "error", "message": "Expected JSON"}), 400

        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "Empty data"}), 400

        try:
            entries = data.get('entry', [])
            if not entries:
                return jsonify({"status": "success", "message": "No entries"}), 200

            for entry in entries:
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    
                    # استقبال الرسائل الواردة بجميع أنواعها
                    for msg in value.get('messages', []):
                        sender = ''.join(filter(str.isdigit, msg.get('from', '')))
                        wamid = msg.get('id')
                        msg_type = msg.get('type', 'text')
                        
                        msg_body = ""
                        if msg_type == 'text':
                            msg_body = msg.get('text', {}).get('body', '')
                        elif msg_type == 'image':
                            msg_body = "[صورة]"
                        elif msg_type == 'video':
                            msg_body = "[فيديو]"
                        elif msg_type == 'audio':
                            msg_body = "[صوت]"
                        elif msg_type == 'document':
                            msg_body = "[مستند]"
                        elif msg_type == 'sticker':
                            msg_body = "[ملصق]"
                        elif msg_type == 'location':
                            msg_body = "[موقع]"
                        else:
                            msg_body = f"[رسالة نوع {msg_type}]"

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

                    # استقبال تحديثات الحالة (قراءة/تسليم)
                    for st in value.get('statuses', []):
                        wamid = st.get('id')
                        status_type = st.get('status')
                        msg_log = WhatsAppMessageLog.query.filter_by(wamid=wamid).first()
                        if msg_log:
                            msg_log.status = status_type
                            db.session.commit()

        except Exception as e:
            current_app.logger.error(f"Webhook error: {str(e)}")
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 200

        return jsonify({"status": "success"}), 200


@whatsapp_bp.route('/webhook-handler', methods=['GET', 'POST'])
def whatsapp_webhook_handler():
    return webhook_handler()


@whatsapp_bp.route('/settings/save', methods=['POST'])
def settings_save():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "No data"}), 400

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

        return jsonify({"success": True, "message": "تم حفظ الإعدادات"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
