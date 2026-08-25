# coding: utf-8
# 📂 apps/whatsapp_service/routes.py

from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from apps.models.whatsapp_models import (
    db, 
    WhatsAppCustomerContact, 
    WhatsAppMessageLog, 
    WhatsAppSettings, 
    WhatsAppWebhookEvent
)
# استيراد دوال الإرسال الاحترافية الجاهزة لديك
from apps.whatsapp_service.whatsapp_api import send_text_message

whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    url_prefix='/whatsapp',  # تم اعتماده بدون بادئة admin ليصبح الرابط /whatsapp/... مباشرة
    template_folder='templates'
)

@whatsapp_bp.route('/', methods=['GET', 'POST'])
def whatsapp_dashboard():
    """لوحة تحكم موحدة تدار عبر تبويبات داخل قالب HTML مفرد بالكامل."""
    active_tab = request.args.get('tab', 'chat')
    contact_id = request.args.get('contact_id', type=int)
    
    # جلب الإعدادات عبر نظام المفتاح والقيمة (Key-Value)
    phone_number_id = WhatsAppSettings.get_setting('WHATSAPP_PHONE_NUMBER_ID', '1336881386166971')
    access_token = WhatsAppSettings.get_setting('WHATSAPP_ACCESS_TOKEN', '')
    verify_token = WhatsAppSettings.get_setting('WHATSAPP_VERIFY_TOKEN', 'mahjoob_webhook_secret_2026')
        
    contacts = WhatsAppCustomerContact.query.order_by(WhatsAppCustomerContact.last_timestamp.desc()).all()
    logs = WhatsAppMessageLog.query.order_by(WhatsAppMessageLog.timestamp.desc()).limit(50).all()
    
    selected_contact = None
    messages = []

    if contact_id:
        selected_contact = WhatsAppCustomerContact.query.get(contact_id)
        if selected_contact:
            # جلب الرسائل المرتبطة برقم هاتف العميل
            messages = WhatsAppMessageLog.query.filter(
                (WhatsAppMessageLog.sender_number == selected_contact.phone) | 
                (WhatsAppMessageLog.recipient_number == selected_contact.phone)
            ).order_by(WhatsAppMessageLog.timestamp.asc()).all()
            
            # تصفير عداد غير المقروء عند فتح المحادثة
            if selected_contact.unread_count and selected_contact.unread_count > 0:
                selected_contact.unread_count = 0
                db.session.commit()

    # معالجة حفظ الإعدادات من تبويب الإعدادات
    if request.method == 'POST' and active_tab == 'settings':
        new_phone_id = request.form.get('whatsapp_phone_number_id')
        new_token = request.form.get('whatsapp_token')
        
        WhatsAppSettings.set_setting('WHATSAPP_PHONE_NUMBER_ID', new_phone_id)
        WhatsAppSettings.set_setting('WHATSAPP_ACCESS_TOKEN', new_token)
        
        flash('تم حفظ الإعدادات بنجاح', 'success')
        return redirect(url_for('whatsapp_service.whatsapp_dashboard', tab='settings'))

    # معالجة إرسال رسالة جديدة عبر HTMX باستخدام دالة send_text_message الجاهزة
    if request.method == 'POST' and active_tab == 'chat':
        phone = request.form.get('phone')
        message_text = request.form.get('message')
        
        # التأكد من جلب العميل في حال لم يكن محفزاً بالاعلى لضمان عدم حدوث خطأ 400
        target_contact = selected_contact
        if not target_contact and phone:
            target_contact = WhatsAppCustomerContact.query.filter_by(phone=phone).first()

        if message_text and phone and target_contact:
            # استخدام دالة الإرسال المركزية من whatsapp_api.py (تتولى الإرسال والتسجيل في قاعدة البيانات تلقائياً)
            success, res_data = send_text_message(phone, message_text)
            
            # إرجاع مقتطف HTML للرسالة عبر HTMX للتحديث اللحظي الفوري في واجهة المستخدم
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return f'''
                <div class="message-item flex justify-start">
                  <div class="max-w-[75%] bg-[#570575]/40 border border-[#570575]/50 rounded-lg px-3 py-1.5 shadow-md text-xs text-[#e9edef] relative">
                    <p class="whitespace-pre-wrap leading-relaxed pt-0.5 pb-1">{message_text}</p>
                    <div class="flex items-center justify-end gap-1 float-left ml-1 mt-[-6px]">
                      <span class="text-[9px] text-[#e9edef]/60">{datetime.now().strftime('%I:%M %p')}</span>
                      <span class="text-[10px] font-bold text-[#D4AF37]">{'✓✓' if success else '❌'}</span>
                    </div>
                  </div>
                </div>
                '''

    return render_template(
        'admin/whatsapp/whatsapp_dashboard.html',
        active_tab=active_tab,
        phone_number_id=phone_number_id,
        access_token=access_token,
        verify_token=verify_token,
        contacts=contacts,
        selected_contact=selected_contact,
        messages=messages,
        logs=logs
    )


@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
def webhook_handler():
    """مستقبل الويب هوك للتعامل مع الرسائل الواردة وتحديثات حالة Meta API"""
    verify_token = WhatsAppSettings.get_setting('WHATSAPP_VERIFY_TOKEN', 'mahjoob_webhook_secret_2026')

    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode and token:
            if token == verify_token:
                return challenge, 200
            return 'Forbidden', 403
        return 'Bad Request', 400
        
    elif request.method == 'POST':
        data = request.json
        
        # حفظ الحدث الخام في جدول Webhook Events للتتبع
        try:
            webhook_event = WhatsAppWebhookEvent(
                event_type='messages_webhook',
                payload=data,
                processed=False
            )
            db.session.add(webhook_event)
            db.session.commit()
        except Exception:
            db.session.rollback()

        try:
            entry = data.get('entry', [])[0]
            changes = entry.get('changes', [])[0]
            value = changes.get('value', {})
            
            # معالجة الرسائل الواردة من العملاء
            if 'messages' in value:
                msg_data = value['messages'][0]
                phone = msg_data.get('from')
                wamid = msg_data.get('id')
                msg_body = msg_data.get('text', {}).get('body', '')
                profile_name = value.get('contacts', [{}])[0].get('profile', {}).get('name', f'عميل ({phone})')
                
                # البحث عن جهة الاتصال أو إنشاؤها تلقائياً
                contact = WhatsAppCustomerContact.query.filter_by(phone=phone).first()
                if not contact:
                    contact = WhatsAppCustomerContact(
                        phone=phone,
                        name=profile_name,
                        whatsapp_profile_name=profile_name
                    )
                    db.session.add(contact)
                    db.session.commit()
                
                contact.last_message = msg_body
                contact.last_timestamp = datetime.utcnow()
                contact.unread_count = (contact.unread_count or 0) + 1
                
                # تسجيل الرسالة الواردة في سجل الرسائل
                new_msg = WhatsAppMessageLog(
                    wamid=wamid,
                    direction='inbound',
                    sender_number=phone,
                    recipient_number=WhatsAppSettings.get_setting('WHATSAPP_PHONE_NUMBER_ID', '1336881386166971'),
                    customer_id=contact.id,
                    message_type='text',
                    content=msg_body,
                    status='received'
                )
                
                db.session.add(new_msg)
                db.session.commit()
                
                webhook_event.processed = True
                db.session.commit()
                
        except Exception as e:
            print("Error parsing webhook payload:", e)
            
        return jsonify({"status": "success"}), 200
