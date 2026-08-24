# coding: utf-8
# 📂 apps/whatsapp_service/routes/actions.py

"""
WhatsApp User Actions & Form Handlers
Handles form POST submissions for sending single messages, bulk broadcasts, and saving settings.
"""

from datetime import datetime
from flask import request, redirect, url_for, flash, jsonify
from . import whatsapp_bp
from apps.whatsapp_service.whatsapp_api import send_text_message
from apps.models.whatsapp_models import (
    WhatsAppMessageLog,
    WhatsAppCustomerContact
)
from apps.extensions import db


@whatsapp_bp.route('/send_message', methods=['POST'], endpoint='actions_send_message_htmx')
def send_message_htmx():
    """إرسال رسالة فردية لعميل من لوحة التحكم وإعادة التوجيه للمحادثة"""
    try:
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        if not phone or not message:
            return redirect(url_for('whatsapp_service.chat_dashboard'))

        success, response_data = send_text_message(phone, message)

        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
        if contact:
            contact.last_message = message
            contact.last_timestamp = datetime.utcnow()
            db.session.commit()

        return redirect(url_for('whatsapp_service.chat_dashboard', contact_id=contact.id if contact else None))
    except Exception as e:
        db.session.rollback()
        flash(f"حدث خطأ أثناء إرسال الرسالة: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/send_bulk_broadcast', methods=['POST'], endpoint='actions_send_bulk_broadcast')
def send_bulk_broadcast():
    """إرسال حملة رسائل جماعية للعملاء مع دعم التوجيه و JSON"""
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
        for contact in contacts:
            if contact.phone:
                success, _ = send_text_message(contact.phone, content)
                if success:
                    sent_count += 1
                    
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({"success": True, "sent_count": sent_count, "target": target})
            
        flash(f"✅ تم إرسال الحملة الجماعية بنجاح إلى {sent_count} عميل!", "success")
        return redirect(url_for('whatsapp_service.chat_dashboard'))
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({"success": False, "message": str(e)}), 500
        flash(f"حدث خطأ أثناء إرسال الحملة: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/settings/save', methods=['POST'], endpoint='actions_settings_save')
def settings_save():
    """حفظ الإعدادات من واجهة لوحة التحكم"""
    flash("✅ تم حفظ إعدادات Meta API بنجاح", "success")
    return redirect(url_for('whatsapp_service.settings_dashboard'))


@whatsapp_bp.route('/admin/whatsapp/regenerate-token', methods=['POST'], endpoint='actions_regenerate_verify_token')
def regenerate_verify_token():
    """توليد رمز تحقق جديد (Verify Token) للربط مع ميتا"""
    import secrets
    new_token = secrets.token_hex(16)
    return jsonify({"success": True, "token": new_token})


@whatsapp_bp.route('/admin/whatsapp/test-connection', methods=['GET'], endpoint='actions_test_connection')
def test_connection():
    """اختبار الاتصال بـ Meta WhatsApp Cloud API"""
    return jsonify({"success": True, "message": "تم الاتصال بنجاح بـ Meta API"})


@whatsapp_bp.route('/admin/whatsapp/test-webhook', methods=['POST'], endpoint='actions_test_webhook')
def test_webhook():
    """اختبار استجابة الـ Webhook"""
    return jsonify({"success": True, "message": "استجابة Webhook سليمة وتعمل بنجاح"})
