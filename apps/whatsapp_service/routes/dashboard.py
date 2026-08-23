# coding: utf-8
# 📂 apps/whatsapp_service/routes/dashboard.py

"""
WhatsApp Service Dashboard & UI Routes Module for Mahjoub Online WebApp
"""

from datetime import datetime
from flask import render_template, request, jsonify, flash, redirect, url_for, current_app
from apps.extensions import db
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog
from apps.whatsapp_service.whatsapp_api import send_meta_whatsapp_message
from . import whatsapp_bp


@whatsapp_bp.route('/dashboard', methods=['GET'])
@whatsapp_bp.route('/dashboard/<int:contact_id>', methods=['GET'])
def chat_dashboard(contact_id=None):
    """لوحة المحادثات المباشرة والرئيسية للواتساب"""
    try:
        contacts = WhatsAppCustomerContact.query.order_by(
            WhatsAppCustomerContact.last_timestamp.desc()
        ).all()

        target_id = contact_id or request.args.get('contact_id', type=int)
        current_contact = None
        messages = []

        if target_id:
            current_contact = WhatsAppCustomerContact.query.get(target_id)
        elif contacts:
            current_contact = contacts[0]

        if current_contact:
            messages = WhatsAppMessageLog.query.filter(
                (WhatsAppMessageLog.sender_number == current_contact.phone) |
                (WhatsAppMessageLog.recipient_number == current_contact.phone)
            ).order_by(WhatsAppMessageLog.timestamp.asc()).all()

        return render_template(
            'admin/dashboard.html',
            active_tab='chat',
            contacts=contacts,
            selected_contact=current_contact,
            messages=messages
        )
    except Exception as e:
        current_app.logger.error(f"⚠️ [Chat Dashboard Error]: {e}")
        return render_template(
            'admin/dashboard.html',
            active_tab='chat',
            contacts=[],
            selected_contact=None,
            messages=[]
        )


@whatsapp_bp.route('/send-message-htmx', methods=['POST'])
def send_message_htmx():
    """إرسال رسالة فردية ومعالجتها عبر HTMX بدون إعادة تحميل الصفحة"""
    phone = request.form.get('phone')
    message_text = request.form.get('message', '').strip()

    if not phone or not message_text:
        return "<div class='text-red-500 text-xs p-2'>⚠️ يرجى كتابة الرسالة قبل الإرسال</div>", 400

    try:
        # 1. إرسال الرسالة عبر Meta API
        api_response = send_meta_whatsapp_message(phone, message_text)

        # 2. تسجيل الرسالة في قاعدة البيانات
        new_log = WhatsAppMessageLog(
            sender_number=current_app.config.get('WHATSAPP_PHONE_NUMBER', 'SYSTEM'),
            recipient_number=phone,
            content=message_text,
            direction='outbound',
            message_type='text',
            status='sent',
            timestamp=datetime.utcnow()
        )
        db.session.add(new_log)

        # تحديث آخر ظهور لجهة الاتصال
        contact = WhatsAppCustomerContact.query.filter_by(phone=phone).first()
        if contact:
            contact.last_message = message_text
            contact.last_timestamp = datetime.utcnow()
            
        db.session.commit()

        # 3. إرجاع مكون HTML المباشر لـ HTMX (تم الحفاظ على ألوان التصميم الخاصة بك)
        time_str = datetime.now().strftime('%I:%M %p')
        return f'''
        <div class="max-w-md self-end bg-[#570575] text-white p-3.5 rounded-2xl rounded-tl-none text-xs md:text-sm shadow-xs">
          <p class="leading-relaxed whitespace-pre-wrap">{message_text}</p>
          <div class="text-[10px] text-purple-200 mt-1.5 text-left font-mono">
            🕒 {time_str}
          </div>
        </div>
        '''
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"⚠️ [Send HTMX Error]: {e}")
        return f"<div class='text-red-500 text-xs p-2'>❌ فشل إرسال الرسالة: {str(e)}</div>", 500


@whatsapp_bp.route('/send-bulk-broadcast', methods=['POST'])
def send_bulk_broadcast():
    """معالجة حملات الإرسال الجماعي"""
    target_group = request.form.get('target_group')
    custom_message = request.form.get('custom_message', '').strip()

    if not custom_message:
        return jsonify({"success": False, "error": "محتوى الرسالة فارغ"}), 400

    try:
        # جلب قائمة العملاء المستهدفين
        query = WhatsAppCustomerContact.query
        if target_group == 'recent_orders':
            query = query.filter(WhatsAppCustomerContact.orders.any())
            
        target_contacts = query.all()
        sent_count = 0

        for contact in target_contacts:
            res = send_meta_whatsapp_message(contact.phone, custom_message)
            if res.get('messages'):
                sent_count += 1

        return jsonify({
            "success": True,
            "sent_count": sent_count,
            "message": f"تم إرسال الحملة بنجاح إلى {sent_count} عميل."
        })
    except Exception as e:
        current_app.logger.error(f"⚠️ [Broadcast Error]: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@whatsapp_bp.route('/start-new-chat', methods=['POST'])
def start_new_chat():
    """بدء محادثة جديدة مع رقم هاتف محدد"""
    phone = request.form.get('phone', '').strip()
    message = request.form.get('message', '').strip()

    if not phone:
        flash("يرجى إدخال رقم الهاتف بشكل صحيح", "danger")
        return redirect(url_for('whatsapp.chat_dashboard'))

    try:
        contact = WhatsAppCustomerContact.query.filter_by(phone=phone).first()
        if not contact:
            contact = WhatsAppCustomerContact(phone=phone, name=phone, last_message=message)
            db.session.add(contact)
            db.session.commit()

        if message:
            send_meta_whatsapp_message(phone, message)

        flash("تم فتح المحادثة بنجاح", "success")
        return redirect(url_for('whatsapp.chat_dashboard', contact_id=contact.id))
    except Exception as e:
        db.session.rollback()
        flash(f"حدث خطأ أثناء فتح المحادثة: {e}", "danger")
        return redirect(url_for('whatsapp.chat_dashboard'))


@whatsapp_bp.route('/logs', methods=['GET'])
def logs_dashboard():
    """لوحة سجل الرسائل والـ Logs"""
    try:
        logs = WhatsAppMessageLog.query.order_by(
            WhatsAppMessageLog.timestamp.desc()
        ).limit(150).all()
        return render_template(
            'admin/dashboard.html',
            active_tab='logs',
            logs=logs
        )
    except Exception as e:
        current_app.logger.error(f"⚠️ [Logs Dashboard Error]: {e}")
        return render_template(
            'admin/dashboard.html',
            active_tab='logs',
            logs=[]
        )


@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_dashboard():
    """لوحة إعدادات Meta WhatsApp API"""
    if request.method == 'POST':
        current_app.config['WHATSAPP_PHONE_NUMBER_ID'] = request.form.get('phone_number_id')
        current_app.config['WHATSAPP_BUSINESS_ACCOUNT_ID'] = request.form.get('business_account_id')
        current_app.config['WHATSAPP_ACCESS_TOKEN'] = request.form.get('access_token')

        flash("تم حفظ إعدادات Meta API بنجاح", "success")
        return redirect(url_for('whatsapp.settings_dashboard', saved='true'))

        # ملاحظة: في بيئة الإنتاج يفضل حفظ هذه القيم في قاعدة البيانات (جدول الإعدادات) 
        # بدلاً من current_app.config لضمان استمراريتها بعد إعادة تشغيل الخادم.

    return render_template(
        'admin/dashboard.html',
        active_tab='settings',
        settings={
            "phone_number_id": current_app.config.get('WHATSAPP_PHONE_NUMBER_ID', ''),
            "whatsapp_business_id": current_app.config.get('WHATSAPP_BUSINESS_ACCOUNT_ID', ''),
            "access_token": current_app.config.get('WHATSAPP_ACCESS_TOKEN', ''),
            "verify_token": current_app.config.get('WHATSAPP_VERIFY_TOKEN', '')
        },
        saved_success=request.args.get('saved') == 'true'
    )
