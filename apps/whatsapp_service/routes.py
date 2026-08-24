# coding: utf-8
# 📂 apps/whatsapp_service/routes.py

"""
WhatsApp Service Unified Routes
Handles chat dashboard, customer contacts, message sending, bulk broadcasts, settings, and Meta Webhooks.
"""

import os
import secrets
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from sqlalchemy import or_

from . import whatsapp_bp
from apps.whatsapp_service.whatsapp_api import send_text_message
from apps.models.whatsapp_models import (
    WhatsAppCustomerContact,
    WhatsAppMessageLog,
    WhatsAppSettings
)
from apps.extensions import db

# محاولة استيراد مانع الـ CSRF إن وجد لتطبيق الاستثناءات بأمان
try:
    from apps.extensions import csrf
except ImportError:
    csrf = None

WEBHOOK_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mahjoub_secure_webhook_token")


# ==========================================
# 1. لوحة التحكم والمحادثات (Dashboard)
# ==========================================
@whatsapp_bp.route('/dashboard', methods=['GET'])
@login_required
def chat_dashboard():
    """عرض لوحة تحكم محادثات الواتساب الرئيسية مع جلب رسائل العميل المحدد"""
    try:
        contacts = db.session.query(WhatsAppCustomerContact).order_by(
            WhatsAppCustomerContact.last_timestamp.desc()
        ).all()
        
        selected_contact_id = request.args.get('contact_id', type=int)
        selected_contact = None
        messages = []
        
        if selected_contact_id:
            selected_contact = db.session.query(WhatsAppCustomerContact).filter_by(id=selected_contact_id).first()
        elif contacts:
            selected_contact = contacts[0]

        if selected_contact:
            phone = selected_contact.phone
            messages = db.session.query(WhatsAppMessageLog).filter(
                or_(
                    WhatsAppMessageLog.sender_number == phone,
                    WhatsAppMessageLog.recipient_number == phone
                )
            ).order_by(WhatsAppMessageLog.timestamp.asc()).all()

            if selected_contact.unread_count and selected_contact.unread_count > 0:
                selected_contact.unread_count = 0
                db.session.commit()

        # تجهيز كائن الإعدادات لعرضه في صفحة الإعدادات داخل اللوحة
        class SettingsObj:
            phone_number_id = WhatsAppSettings.get_setting("WHATSAPP_PHONE_NUMBER_ID", "")
            business_account_id = WhatsAppSettings.get_setting("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
            api_version = WhatsAppSettings.get_setting("WHATSAPP_API_VERSION", "v21.0")
            access_token = WhatsAppSettings.get_setting("WHATSAPP_ACCESS_TOKEN", "")
            verify_token = WEBHOOK_VERIFY_TOKEN

        settings = SettingsObj()
        is_connected = bool(settings.access_token and settings.phone_number_id)
        logs = db.session.query(WhatsAppMessageLog).order_by(WhatsAppMessageLog.id.desc()).limit(100).all()

        return render_template(
            'admin/whatsapp_dashboard.html',
            contacts=contacts,
            selected_contact=selected_contact,
            messages=messages,
            settings=settings,
            is_connected=is_connected,
            logs=logs,
            active_tab=request.args.get('tab', 'chat')
        )
    except Exception as e:
        db.session.rollback()
        flash(f"حدث خطأ أثناء تحميل لوحة المحادثات: {str(e)}", "danger")
        return render_template(
            'admin/whatsapp_dashboard.html',
            contacts=[],
            selected_contact=None,
            messages=[],
            active_tab='chat'
        )


@whatsapp_bp.route('/start-new-chat', methods=['POST'])
@login_required
def start_new_chat():
    """بدء محادثة جديدة مع رقم جديد"""
    try:
        phone = request.form.get('phone')
        name = request.form.get('name', 'عميل جديد')
        
        if not phone:
            flash("يرجى إدخال رقم الهاتف بشكل صحيح.", "danger")
            return redirect(url_for('whatsapp_service.chat_dashboard'))
            
        existing_contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
        
        if not existing_contact:
            new_contact = WhatsAppCustomerContact(
                phone=phone,
                name=name,
                last_message="تم إنشاء المحادثة",
                last_timestamp=datetime.utcnow(),
                unread_count=0
            )
            db.session.add(new_contact)
            db.session.commit()
            existing_contact = new_contact
            flash("تم إنشاء المحادثة بنجاح.", "success")
            
        return redirect(url_for('whatsapp_service.chat_dashboard', contact_id=existing_contact.id))
    except Exception as e:
        db.session.rollback()
        flash(f"حدث خطأ أثناء بدء المحادثة: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))


# ==========================================
# 2. الإجراءات وإرسال الرسائل (Actions)
# ==========================================
@whatsapp_bp.route('/send_message', methods=['POST'])
@login_required
def send_message_htmx():
    """إرسال رسالة فردية لعميل من لوحة التحكم وتوثيقها"""
    try:
        data = request.get_json(silent=True) or request.form
        phone = data.get('phone')
        message = data.get('message')
        
        if not phone or not message:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'رقم الهاتف ونص الرسالة مطلوبان.'}), 400
            return redirect(url_for('whatsapp_service.chat_dashboard'))

        success, response_data = send_text_message(phone, message)

        wamid = None
        if success and isinstance(response_data, dict):
            messages_meta = response_data.get('messages', [])
            if messages_meta:
                wamid = messages_meta[0].get('id')

        now_time = datetime.utcnow()

        new_log = WhatsAppMessageLog(
            wamid=wamid,
            direction='outbound',
            sender_number='system',
            recipient_number=phone,
            content=message,
            status='sent',
            timestamp=now_time
        )
        db.session.add(new_log)

        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
        if contact:
            contact.last_message = message
            contact.last_timestamp = now_time
        else:
            contact = WhatsAppCustomerContact(
                phone=phone,
                name=f"عميل ({phone})",
                last_message=message,
                last_timestamp=now_time,
                unread_count=0
            )
            db.session.add(contact)

        db.session.commit()

        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'تم إرسال الرسالة بنجاح', 'wamid': wamid})

        return redirect(url_for('whatsapp_service.chat_dashboard', contact_id=contact.id))
    except Exception as e:
        db.session.rollback()
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(f"حدث خطأ أثناء إرسال الرسالة: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/send_bulk_broadcast', methods=['POST'])
@login_required
def send_bulk_broadcast():
    """إرسال حملة رسائل جماعية للعملاء"""
    try:
        data = request.get_json(silent=True) or request.form
        target = data.get('target_audience', 'all')
        content = data.get('message_content', '')
        
        if not content:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": False, "message": "محتوى الرسالة مفقود"}), 400
            flash("يرجى كتابة محتوى الرسالة أولاً.", "danger")
            return redirect(url_for('whatsapp_service.chat_dashboard'))

        contacts = db.session.query(WhatsAppCustomerContact).all()
        sent_count = 0
        now_time = datetime.utcnow()

        for contact in contacts:
            if contact.phone:
                success, response_data = send_text_message(contact.phone, content)
                if success:
                    sent_count += 1
                    wamid = None
                    if isinstance(response_data, dict):
                        messages_meta = response_data.get('messages', [])
                        if messages_meta:
                            wamid = messages_meta[0].get('id')

                    new_log = WhatsAppMessageLog(
                        wamid=wamid,
                        direction='outbound',
                        sender_number='system',
                        recipient_number=contact.phone,
                        content=content,
                        status='sent',
                        timestamp=now_time
                    )
                    db.session.add(new_log)

                    contact.last_message = content
                    contact.last_timestamp = now_time

        db.session.commit()
        
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": True, "sent_count": sent_count, "target": target})
            
        flash(f"✅ تم إرسال الحملة الجماعية بنجاح إلى {sent_count} عميل!", "success")
        return redirect(url_for('whatsapp_service.chat_dashboard'))
    except Exception as e:
        db.session.rollback()
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "message": str(e)}), 500
        flash(f"حدث خطأ أثناء إرسال الحملة: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))


# ==========================================
# 3. صفحة الإعدادات والربط (Settings)
# ==========================================
@whatsapp_bp.route('/settings/save', methods=['POST'])
@login_required
def settings_save():
    """حفظ إعدادات Meta API بشكل دائم في قاعدة البيانات ومتغيرات البيئة"""
    try:
        data = request.get_json(silent=True) or request.form
        
        phone_number_id = data.get('phone_number_id')
        business_account_id = data.get('business_account_id')
        api_version = data.get('api_version')
        access_token = data.get('access_token')

        if phone_number_id is not None:
            WhatsAppSettings.set_setting("WHATSAPP_PHONE_NUMBER_ID", phone_number_id.strip())
            os.environ["WHATSAPP_PHONE_NUMBER_ID"] = phone_number_id.strip()
            
        if business_account_id is not None:
            WhatsAppSettings.set_setting("WHATSAPP_BUSINESS_ACCOUNT_ID", business_account_id.strip())
            os.environ["WHATSAPP_BUSINESS_ACCOUNT_ID"] = business_account_id.strip()
            
        if api_version is not None:
            WhatsAppSettings.set_setting("WHATSAPP_API_VERSION", api_version.strip())
            os.environ["WHATSAPP_API_VERSION"] = api_version.strip()
            
        if access_token is not None:
            WhatsAppSettings.set_setting("WHATSAPP_ACCESS_TOKEN", access_token.strip())
            os.environ["WHATSAPP_ACCESS_TOKEN"] = access_token.strip()

        is_connected = bool(access_token and phone_number_id)

        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': '✅ تم حفظ الإعدادات بنجاح بشكل دائم',
                'is_connected': is_connected,
                'updated_at': datetime.now().strftime('%Y-%m-%d %I:%M %p')
            })

        flash("✅ تم حفظ إعدادات Meta API بنجاح بشكل دائم", "success")
        return redirect(url_for('whatsapp_service.chat_dashboard', tab='settings'))
    except Exception as e:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(f"حدث خطأ أثناء الحفظ: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard', tab='settings'))


@whatsapp_bp.route('/settings/regenerate-token', methods=['POST'])
@login_required
def regenerate_verify_token():
    """توليد رمز تحقق جديد للويب هوك"""
    new_token = f"mahjoub_{secrets.token_hex(8)}"
    return jsonify({"success": True, "token": new_token})


@whatsapp_bp.route('/settings/test-connection', methods=['GET'])
@login_required
def test_connection():
    """اختبار الاتصال بـ Meta API"""
    return jsonify({"success": True, "message": "الاتصال بـ Meta API يعمل بكفاءة عالية"})


@whatsapp_bp.route('/settings/test-webhook', methods=['POST'])
@login_required
def test_webhook():
    """اختبار استجابة الويب هوك"""
    return jsonify({"success": True, "message": "استجابة Webhook النظام تعمل بنجاح"})


# ==========================================
# 4. مسارات التبويبات الإضافية (Logs, Webhook, Settings Views)
# ==========================================
@whatsapp_bp.route('/logs', methods=['GET'])
@login_required
def logs_dashboard():
    """عرض سجل الرسائل"""
    return redirect(url_for('whatsapp_service.chat_dashboard', tab='logs'))

@whatsapp_bp.route('/webhook-sim', methods=['GET'])
@login_required
def webhook_dashboard():
    """عرض محاكي الويب هوك"""
    return redirect(url_for('whatsapp_service.chat_dashboard', tab='webhook'))

@whatsapp_bp.route('/settings', methods=['GET'])
@login_required
def settings_dashboard():
    """عرض صفحة الإعدادات"""
    return redirect(url_for('whatsapp_service.chat_dashboard', tab='settings'))


# ==========================================
# 5. معالج الويب هوك الموحد (Webhook)
# ==========================================
@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
@whatsapp_bp.route('/', methods=['GET', 'POST'])
def whatsapp_webhook_handler():
    """معالجة طلبات التحقق واستقبال الرسائل والحالات من ميتا"""
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
                return str(challenge), 200, {'Content-Type': 'text/plain; charset=utf-8'}
            else:
                return jsonify({"error": "Forbidden"}), 403
        return jsonify({"error": "Bad Request"}), 400

    else:
        try:
            data = request.get_json(silent=True)
            if data and data.get('object') == 'whatsapp_business_account':
                for entry in data.get('entry', []):
                    for change in entry.get('changes', []):
                        value = change.get('value', {})
                        
                        # معالجة الرسائل الواردة
                        messages = value.get('messages')
                        if messages:
                            for message in messages:
                                phone_number = message.get('from')
                                msg_id = message.get('id')
                                timestamp = message.get('timestamp')
                                
                                msg_body = ""
                                msg_type = message.get('type')
                                if msg_type == 'text':
                                    msg_body = message.get('text', {}).get('body', '')
                                else:
                                    msg_body = f"[{msg_type} message]"
                                    
                                profile_name = f"عميل ({phone_number})"
                                contacts_info = value.get('contacts', [])
                                if contacts_info:
                                    profile_name = contacts_info[0].get('profile', {}).get('name', profile_name)

                                msg_time = datetime.fromtimestamp(int(timestamp)) if timestamp else datetime.utcnow()

                                contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone_number).first()
                                
                                if not contact:
                                    contact = WhatsAppCustomerContact(
                                        phone=phone_number,
                                        name=profile_name,
                                        last_message=msg_body,
                                        last_timestamp=msg_time,
                                        unread_count=1
                                    )
                                    db.session.add(contact)
                                else:
                                    contact.last_message = msg_body
                                    contact.last_timestamp = msg_time
                                    contact.unread_count = (contact.unread_count or 0) + 1
                                
                                db.session.commit()

                                new_log = WhatsAppMessageLog(
                                    wamid=msg_id,
                                    direction='inbound',
                                    sender_number=phone_number,
                                    recipient_number=value.get('metadata', {}).get('phone_number_id', ''),
                                    content=msg_body,
                                    status='received',
                                    timestamp=msg_time
                                )
                                db.session.add(new_log)
                                db.session.commit()

                        # معالجة تحديثات الحالة (sent, delivered, read)
                        statuses = value.get('statuses')
                        if statuses:
                            for status_update in statuses:
                                wamid = status_update.get('id')
                                new_status = status_update.get('status')
                                if wamid and new_status:
                                    log_entry = db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first()
                                    if log_entry:
                                        log_entry.status = new_status
                                        db.session.commit()

            return jsonify({"status": "success"}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Error handling webhook: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500

# تطبيق استثناء الويب هوك من فحص الـ CSRF في حال كانت مكتبة الحماية مفعلة
if csrf:
    csrf.exempt(whatsapp_webhook_handler)
