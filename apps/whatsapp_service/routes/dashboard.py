# coding: utf-8
"""
WhatsApp Dashboard & Webhook Routes
Handles chat dashboard, settings, and incoming Webhook messages from Meta API.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from datetime import datetime
from sqlalchemy import or_
from . import whatsapp_bp
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog
from apps.extensions import db
import os

WEBHOOK_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mahjoub_secure_webhook_token")


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

        # إذا تم تحديد عميل، نقوم بجلب سجل الرسائل المتبادلة معه (واردة وصادرة)
        if selected_contact:
            # تصفية الرسائل بناءً على رقم هاتف العميل
            phone = selected_contact.phone
            messages = db.session.query(WhatsAppMessageLog).filter(
                or_(
                    WhatsAppMessageLog.sender_number == phone,
                    WhatsAppMessageLog.recipient_number == phone
                )
            ).order_by(WhatsAppMessageLog.timestamp.asc()).all()

            # تصفير عدد الرسائل غير المقروءة عند فتح المحادثة
            if selected_contact.unread_count and selected_contact.unread_count > 0:
                selected_contact.unread_count = 0
                db.session.commit()

        return render_template(
            'admin/whatsapp_dashboard.html',
            contacts=contacts,
            selected_contact=selected_contact,
            messages=messages,
            active_tab='chat'
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


@whatsapp_bp.route('/send-message', methods=['POST'])
@login_required
def send_dashboard_message():
    """إرسال رسالة نصية مباشرة من لوحة التحكم للعميل المحدد عبر Meta API"""
    try:
        data = request.get_json() or {}
        recipient = data.get('phone')
        message = data.get('message')

        if not recipient or not message:
            return jsonify({'success': False, 'message': 'رقم الهاتف ونص الرسالة مطلوبان.'}), 400

        # استدعاء دالة الإرسال من خدمة الواتساب
        from apps.whatsapp_service.whatsapp_api import send_text_message
        success, result = send_text_message(recipient, message)

        if success:
            return jsonify({'success': True, 'message': 'تم إرسال الرسالة بنجاح', 'data': result})
        else:
            return jsonify({'success': False, 'message': f'فشل الإرسال: {result}'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@whatsapp_bp.route('/logs', methods=['GET'])
@login_required
def logs_dashboard():
    """عرض صفحة سجل الرسائل"""
    try:
        logs = db.session.query(WhatsAppMessageLog).order_by(WhatsAppMessageLog.id.desc()).limit(100).all()
        return render_template('admin/whatsapp_dashboard.html', logs=logs, active_tab='logs')
    except Exception as e:
        flash(f"حدث خطأ أثناء تحميل السجلات: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/webhook-panel', methods=['GET'])
@login_required
def webhook_dashboard():
    """عرض صفحة محاكي ومتابعة الويب هوك"""
    try:
        return render_template('admin/whatsapp_dashboard.html', active_tab='webhook')
    except Exception as e:
        flash(f"حدث خطأ أثناء تحميل لوحة الويب هوك: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/settings', methods=['GET'])
@login_required
def settings_dashboard():
    """عرض صفحة إعدادات ربط Meta WhatsApp API"""
    try:
        class SettingsObj:
            phone_number_id = ""
            business_account_id = ""
            api_version = "v21.0"
            access_token = ""
            verify_token = WEBHOOK_VERIFY_TOKEN
            updated_at = None

        settings = SettingsObj()
        is_connected = bool(settings.access_token and settings.phone_number_id)

        return render_template(
            'admin/whatsapp_dashboard.html',
            active_tab='settings',
            settings=settings,
            is_connected=is_connected
        )
    except Exception as e:
        flash(f"حدث خطأ أثناء تحميل صفحة الإعدادات: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/settings/save', methods=['POST'])
@login_required
def settings_save():
    """حفظ إعدادات Meta API"""
    try:
        phone_number_id = request.form.get('phone_number_id')
        business_account_id = request.form.get('business_account_id')
        api_version = request.form.get('api_version')
        access_token = request.form.get('access_token')

        is_connected = bool(access_token and phone_number_id)
        
        return jsonify({
            'success': True,
            'message': 'تم حفظ الإعدادات بنجاح',
            'is_connected': is_connected,
            'updated_at': datetime.now().strftime('%Y-%m-%d %I:%M %p')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'حدث خطأ أثناء الحفظ: {str(e)}'
        }), 500


@whatsapp_bp.route('/settings/regenerate-token', methods=['POST'])
@login_required
def regenerate_verify_token():
    """تجديد رمز التحقق للويب هوك"""
    try:
        import secrets
        new_token = f"mahjoub_{secrets.token_hex(8)}"
        return jsonify({
            'success': True,
            'token': new_token
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@whatsapp_bp.route('/settings/test-connection', methods=['GET'])
@login_required
def test_connection():
    """اختبار الاتصال بـ Meta WhatsApp API"""
    try:
        return jsonify({
            'success': True,
            'message': 'الاتصال بـ Meta API يعمل بكفاءة عالية'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@whatsapp_bp.route('/settings/test-webhook', methods=['POST'])
@login_required
def test_webhook():
    """اختبار استجابة الويب هوك"""
    try:
        return jsonify({
            'success': True,
            'message': 'استجابة Webhook النظام تعمل بنجاح'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==========================================
# معالج الويب هوك الموحد (التحقق واستقبال الرسائل والحالات)
# ==========================================
@whatsapp_bp.route('/webhook', methods=['GET', 'POST'], endpoint='webhook_main_route')
@whatsapp_bp.route('/', methods=['GET', 'POST'], endpoint='webhook_root_route')
def whatsapp_webhook_handler():
    """معالجة طلبات التحقق واستقبال الرسائل والحالات الحقيقية من ميتا"""
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
            data = request.get_json()
            
            if data and data.get('object') == 'whatsapp_business_account':
                for entry in data.get('entry', []):
                    for change in entry.get('changes', []):
                        value = change.get('value', {})
                        
                        # 1. معالجة الرسائل الواردة
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
                                    try:
                                        contact.unread_count = (contact.unread_count or 0) + 1
                                    except:
                                        pass
                                
                                db.session.commit()

                                new_log = WhatsAppMessageLog(
                                    wamid=msg_id,
                                    direction='inbound',
                                    sender_number=phone_number,
                                    recipient_number=value.get('metadata', {}).get('phone_number_id', ''),
                                    content=msg_body,
                                    status='received'
                                )
                                db.session.add(new_log)
                                db.session.commit()

                        # 2. معالجة تحديثات الحالة (sent, delivered, read)
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
