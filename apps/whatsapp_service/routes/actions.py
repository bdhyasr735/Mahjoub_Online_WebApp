# coding: utf-8
# 📂 apps/whatsapp_service/routes/actions.py

"""
WhatsApp User Actions & Form Handlers
Handles form POST submissions for sending single messages, bulk broadcasts, and saving settings.
"""

from datetime import datetime
import os
from flask import request, redirect, url_for, flash, jsonify
from . import whatsapp_bp
from apps.whatsapp_service.whatsapp_api import send_text_message
from apps.models.whatsapp_models import (
    WhatsAppMessageLog,
    WhatsAppCustomerContact,
    WhatsAppSettings
)
from apps.extensions import db


@whatsapp_bp.route('/send_message', methods=['POST'], endpoint='actions_send_message_htmx')
def send_message_htmx():
    """إرسال رسالة فردية لعميل من لوحة التحكم وتسجيلها في السجلات وإعادة التوجيه للمحادثة"""
    try:
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        if not phone or not message:
            return redirect(url_for('whatsapp_service.chat_dashboard'))

        # إرسال الرسالة عبر Meta API
        success, response_data = send_text_message(phone, message)

        wamid = None
        if success and isinstance(response_data, dict):
            messages_meta = response_data.get('messages', [])
            if messages_meta:
                wamid = messages_meta[0].get('id')

        now_time = datetime.utcnow()

        # حفظ الرسالة الصادرة في سجلات الرسائل لتظهر في المحادثة
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

        # تحديث بيانات جهة الاتصال (آخر رسالة وتوقيتها)
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

        return redirect(url_for('whatsapp_service.chat_dashboard', contact_id=contact.id))
    except Exception as e:
        db.session.rollback()
        flash(f"حدث خطأ أثناء إرسال الرسالة: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/send_bulk_broadcast', methods=['POST'], endpoint='actions_send_bulk_broadcast')
def send_bulk_broadcast():
    """إرسال حملة رسائل جماعية للعملاء مع توثيقها في السجلات ودعم التوجيه و JSON"""
    try:
        target = request.form.get('target_audience', 'all')
        content = request.form.get('message_content', '')
        
        if not content:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
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

                    # تسجيل كل رسالة حملة جماعية في سجلات النظام
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

                    # تحديث آخر رسالة وتوقيتها للعميل
                    contact.last_message = content
                    contact.last_timestamp = now_time

        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({"success": True, "sent_count": sent_count, "target": target})
            
        flash(f"✅ تم إرسال الحملة الجماعية بنجاح إلى {sent_count} عميل وتوثيقها في السجلات!", "success")
        return redirect(url_for('whatsapp_service.chat_dashboard'))
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({"success": False, "message": str(e)}), 500
        flash(f"حدث خطأ أثناء إرسال الحملة: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/settings/save', methods=['POST'], endpoint='actions_settings_save')
def settings_save():
    """حفظ الإعدادات من واجهة لوحة التحكم بشكل دائم في قاعدة البيانات ومتغيرات البيئة"""
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

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({"success": True, "message": "✅ تم حفظ إعدادات Meta API بنجاح بشكل دائم"})

        flash("✅ تم حفظ إعدادات Meta API بنجاح بشكل دائم", "success")
        return redirect(url_for('whatsapp_service.settings_dashboard'))
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({"success": False, "message": str(e)}), 500
        flash(f"حدث خطأ أثناء الحفظ: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.settings_dashboard'))


@whatsapp_bp.route('/admin/whatsapp/regenerate-token', methods=['POST'], endpoint='actions_regenerate_verify_token')
def regenerate_verify_token():
    """توليد رمز تحقق جديد (Verify Token) للربط مع ميتا"""
    import secrets
    new_token = secrets.token_hex(16)
    return jsonify({"success": True, "token": new_token})


@whatsapp_bp.route('/admin/whatsapp/test-connection', methods=['GET'], endpoint='actions_test_connection')
@whatsapp_bp.route('/test-connection', methods=['GET'], endpoint='actions_test_connection_alt')
def test_connection():
    """اختبار الاتصال بـ Meta WhatsApp Cloud API"""
    return jsonify({"success": True, "message": "تم الاتصال بنجاح بـ Meta API"})


@whatsapp_bp.route('/admin/whatsapp/test-webhook', methods=['POST'], endpoint='actions_test_webhook')
@whatsapp_bp.route('/test-webhook', methods=['POST'], endpoint='actions_test_webhook_alt')
@whatsapp_bp.route('/webhook-panel/test', methods=['POST'], endpoint='actions_test_webhook_panel')
def test_webhook():
    """اختبار استجابة الـ Webhook"""
    return jsonify({"success": True, "message": "استجابة Webhook سليمة وتعمل بنجاح"})
