# coding: utf-8
# 📂 apps/whatsapp_service/routes/whatsapp_controller.py

import os
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, current_app, redirect, url_for, flash
from sqlalchemy import or_

try:
    from ..whatsapp_api import send_text_message
except ImportError:
    from apps.whatsapp_service.whatsapp_api import send_text_message

from apps.models.whatsapp_models import (
    WhatsAppMessageLog,
    WhatsAppWebhookEvent,
    WhatsAppCustomerContact
)
from apps.extensions import db

logger = logging.getLogger(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.abspath(os.path.join(basedir, '../templates'))

whatsapp_bp = Blueprint('whatsapp_service', __name__, template_folder=template_dir)

# قوالب الرد السريع الاحترافية الخاصة بمنصة محجوب أونلاين
DEFAULT_QUICK_TEMPLATES = [
    {"id": 1, "title": "ترحيب بالعميل", "content": "مرحباً بك في منصة محجوب أونلاين! كيف يمكننا خدمة طلبك وتجربتك التسوقية اليوم؟ 🛍️✨"},
    {"id": 2, "title": "تأكيد الطلب", "content": "تم استلام طلبكم بنجاح في محجوب أونلاين ✅ وسيتم تجهيزه وشحنه في أقرب وقت."},
    {"id": 3, "title": "متابعة الشحن", "content": "طلبك قيد التوصيل حالياً، وسيتواصل معك مندوب الشحن لتسليم الطلب قريباً."},
    {"id": 4, "title": "خدمة الدعم الفني", "content": "نحن هنا لمساعدتك! إذا كان لديك أي استفسار حول المنتجات أو الطلبات، تفضل بطرحه."}
]


def get_verify_token():
    try:
        return current_app.config.get('WHATSAPP_VERIFY_TOKEN') or os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token')
    except RuntimeError:
        return os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token')


# =============================================================================
# 1. WEBHOOK (GET + POST)
# =============================================================================

@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
@whatsapp_bp.route('/webhook-admin', methods=['GET', 'POST'])
@whatsapp_bp.route('/admin/whatsapp/webhook', methods=['GET', 'POST'])
def direct_webhook():
    if request.method == 'GET':
        return verify_webhook()
    return handle_webhook()


def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    verify_token = get_verify_token()
    if mode == 'subscribe' and token == verify_token:
        return str(challenge), 200
    elif challenge and (token == verify_token or not token):
        return str(challenge), 200
    return "Verification token mismatch", 403


def handle_webhook():
    data = request.get_json(silent=True) or {}
    phone_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID') or os.environ.get('WHATSAPP_PHONE_NUMBER_ID', 'system')

    try:
        entries = data.get('entry', [])
        for entry in entries:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if 'messages' in value:
                    for msg in value['messages']:
                        sender = msg.get('from')
                        msg_type = msg.get('type', 'text')
                        wamid = msg.get('id')
                        if msg_type == 'text':
                            text = msg.get('text', {}).get('body', '')
                        else:
                            text = f'[{msg_type} ملف]'
                        contacts_list = value.get('contacts', [])
                        customer_name = f"عميل ({sender})"
                        if contacts_list:
                            profile_name = contacts_list[0].get('profile', {}).get('name')
                            if profile_name:
                                customer_name = profile_name

                        # حفظ الرسالة الواردة
                        log_entry = WhatsAppMessageLog(
                            wamid=wamid,
                            direction='inbound',
                            sender_number=sender,
                            recipient_number=phone_id,
                            message_type=msg_type,
                            content=text,
                            status='received'
                        )
                        db.session.add(log_entry)

                        # تحديث أو إنشاء جهة اتصال
                        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=sender).first()
                        if contact:
                            contact.name = customer_name if not contact.name or contact.name.startswith("عميل (") else contact.name
                            contact.last_message = text
                            contact.last_timestamp = datetime.utcnow()
                            contact.unread_count = (contact.unread_count or 0) + 1
                        else:
                            new_contact = WhatsAppCustomerContact(
                                phone=sender,
                                name=customer_name,
                                last_message=text,
                                last_timestamp=datetime.utcnow(),
                                unread_count=1
                            )
                            db.session.add(new_contact)
                        db.session.commit()

                elif 'statuses' in value:
                    for st in value['statuses']:
                        wamid = st.get('id')
                        status = st.get('status')
                        if wamid:
                            msg_log = db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first()
                            if msg_log:
                                msg_log.status = status
                                db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Webhook error: {e}")

    return jsonify({"status": "EVENT_RECEIVED"}), 200


# =============================================================================
# 2. DASHBOARD (الصفحة الرئيسية)
# =============================================================================

@whatsapp_bp.route('/dashboard')
def chat_dashboard():
    """عرض لوحة التحكم الرئيسية مع جميع جهات الاتصال وعدم فتح أي دردشة إلا عند اختيارها صراحة"""
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
    messages = []
    
    # لا تقم بفتح أو جلب أي محادثة افتراضياً إلا إذا تم اختيار العميل عبر الـ contact_id
    if contact_id:
        current_contact = db.session.query(WhatsAppCustomerContact).get(contact_id)
        if current_contact:
            messages = db.session.query(WhatsAppMessageLog).filter(
                or_(
                    WhatsAppMessageLog.sender_number == current_contact.phone,
                    WhatsAppMessageLog.recipient_number == current_contact.phone
                )
            ).order_by(WhatsAppMessageLog.timestamp.asc()).limit(50).all()

    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='chat',
        contacts=contacts,
        current_contact=current_contact,
        messages=messages
    )


# =============================================================================
# 3. ACTION ENDPOINTS (إرسال الرسائل الفردية والتحديث الديناميكي)
# =============================================================================

@whatsapp_bp.route('/send_message', methods=['POST'])
def send_message_htmx():
    """إرسال رسالة عبر HTMX لإضافتها فوراً بدون وميض وبدون إعادة تحميل الصفحة مع حماية تكرار wamid"""
    phone = request.form.get('phone')
    message_content = request.form.get('message')
    
    if not phone or not message_content:
        return '<div class="text-red-500 text-xs p-2">رقم الهاتف أو نص الرسالة مفقود.</div>', 400

    # إرسال الرسالة عبر Meta API
    success, response_data = send_text_message(phone, message_content)
    
    wamid = None
    if success and isinstance(response_data, dict):
        messages_meta = response_data.get('messages', [])
        if messages_meta:
            wamid = messages_meta[0].get('id')

    phone_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID') or os.environ.get('WHATSAPP_PHONE_NUMBER_ID', 'system')
    
    with db.session.no_autoflush:
        # التأكد من عدم تكرار الـ wamid إذا تم تسجيله مسبقاً عبر Webhook
        if wamid:
            existing_log = db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first()
            if existing_log:
                wamid = None

        # حفظ سجل الرسالة الصادرة
        outbound_log = WhatsAppMessageLog(
            wamid=wamid,
            direction='outbound',
            sender_number=phone_id,
            recipient_number=phone,
            message_type='text',
            content=message_content,
            status='sent' if success else 'failed'
        )
        db.session.add(outbound_log)

        # تحديث بيانات الاتصال للعميل
        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
        if contact:
            contact.last_message = message_content
            contact.last_timestamp = datetime.utcnow()
        
        db.session.commit()

    # إرجاع فقرة HTML المصغرة للرسالة ليتم حقنها مباشرة في واجهة المحادثة
    current_time_str = datetime.utcnow().strftime('%I:%M %p')
    return f"""
    <div class="flex flex-col items-end mb-3 message-bubble">
      <div class="max-w-[70%] bg-[#632C8F] text-white rounded-2xl px-4 py-3 shadow-sm text-sm">
        <p class="leading-relaxed">{message_content}</p>
        <div class="flex items-center justify-end gap-1 mt-1 text-[10px] text-purple-200">
          <span>{current_time_str}</span>
          <i class="fa-solid fa-check-double text-[#D4AF37] text-[10px]"></i>
        </div>
      </div>
    </div>
    """


@whatsapp_bp.route('/update_contact_name/<int:contact_id>', methods=['POST'])
def update_contact_name(contact_id):
    """تعديل اسم العميل مباشرة من لوحة التحكم وحفظه"""
    contact = db.session.query(WhatsAppCustomerContact).get_or_404(contact_id)
    new_name = request.form.get('name')
    
    if new_name:
        contact.name = new_name.strip()
        db.session.commit()
        
    return f'<span class="text-sm font-bold text-slate-800">{contact.name}</span>'


@whatsapp_bp.route('/get_latest_messages/<int:contact_id>', methods=['GET'])
def get_latest_messages(contact_id):
    """جلب الرسائل الجديدة لتحديث الشاشة تلقائياً عبر HTMX Polling"""
    contact = db.session.query(WhatsAppCustomerContact).get_or_404(contact_id)
    
    if contact.unread_count > 0:
        contact.unread_count = 0
        db.session.commit()

    messages = db.session.query(WhatsAppMessageLog).filter(
        or_(
            WhatsAppMessageLog.sender_number == contact.phone,
            WhatsAppMessageLog.recipient_number == contact.phone
        )
    ).order_by(WhatsAppMessageLog.timestamp.asc()).all()

    html_output = ""
    for m in messages:
        is_outgoing = m.direction == 'outbound'
        time_str = m.timestamp.strftime('%I:%M %p') if m.timestamp else ''
        if is_outgoing:
            html_output += f"""
            <div class="flex flex-col items-end mb-3">
              <div class="max-w-[70%] bg-[#632C8F] text-white rounded-2xl px-4 py-3 shadow-sm text-sm">
                <p class="leading-relaxed">{m.content}</p>
                <div class="flex items-center justify-end gap-1 mt-1 text-[10px] text-purple-200">
                  <span>{time_str}</span>
                  <i class="fa-solid fa-check-double text-[#D4AF37] text-[10px]"></i>
                </div>
              </div>
            </div>
            """
        else:
            html_output += f"""
            <div class="flex flex-col items-start mb-3">
              <div class="max-w-[70%] bg-white border border-slate-200 text-slate-800 rounded-2xl px-4 py-3 shadow-sm text-sm">
                <p class="leading-relaxed">{m.content}</p>
                <div class="flex items-center gap-1 mt-1 text-[10px] text-slate-400">
                  <span>{time_str}</span>
                </div>
              </div>
            </div>
            """
    return html_output


# =============================================================================
# 4. BULK BROADCAST (الإرسال الجماعي)
# =============================================================================

@whatsapp_bp.route('/send_bulk_broadcast', methods=['POST'])
def send_bulk_broadcast():
    """إرسال حملة رسائل جماعية للعملاء مع دعم التوجيه و JSON"""
    target = request.form.get('target_audience', 'all')
    content = request.form.get('message_content', '')
    
    contacts = db.session.query(WhatsAppCustomerContact).all()
    
    sent_count = 0
    for contact in contacts:
        if contact.phone and content:
            success, _ = send_text_message(contact.phone, content)
            if success:
                sent_count += 1
                
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({"success": True, "sent_count": sent_count, "target": target})
        
    flash(f"✅ تم إرسال الحملة الجماعية بنجاح إلى {sent_count} عميل عبر محجوب أونلاين!", "success")
    return redirect(url_for('whatsapp_service.chat_dashboard'))


# =============================================================================
# 5. API ENDPOINTS (للاستخدام مع Fetch والقوالب التفاعلية)
# =============================================================================

@whatsapp_bp.route('/api/templates', methods=['GET'])
def get_quick_templates_api():
    """جلب قوالب الرد السريع ديناميكياً لتغذية واجهة لوحة التحكم"""
    return jsonify({
        "success": True,
        "platform": "محجوب أونلاين",
        "templates": DEFAULT_QUICK_TEMPLATES
    })


@whatsapp_bp.route('/api/whatsapp/conversation/<phone>', methods=['GET'])
def get_conversation_data(phone):
    """جلب رسائل عميل معين بصيغة JSON"""
    contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone).first()
    if contact and contact.unread_count > 0:
        contact.unread_count = 0
        db.session.commit()

    messages = db.session.query(WhatsAppMessageLog).filter(
        or_(
            WhatsAppMessageLog.sender_number == phone,
            WhatsAppMessageLog.recipient_number == phone
        )
    ).order_by(WhatsAppMessageLog.timestamp.asc()).all()

    messages_data = []
    for m in messages:
        ts = getattr(m, 'timestamp', None)
        messages_data.append({
            "id": m.id,
            "direction": m.direction,
            "message_body": m.content,
            "message_type": getattr(m, 'message_type', 'text'),
            "timestamp": ts.strftime('%Y-%m-%d %H:%M') if ts else '',
            "status": m.status
        })

    client_info = {
        "name": contact.name if contact else phone,
        "phone": phone
    }

    return jsonify({
        "success": True,
        "client": client_info,
        "messages": messages_data
    })


@whatsapp_bp.route('/api/whatsapp/send', methods=['POST'])
def send_message_api():
    """إرسال رسالة عبر JSON"""
    data = request.get_json(silent=True) or {}
    phone = data.get('phone')
    message = data.get('message')
    if not phone or not message:
        return jsonify({"success": False, "error": "بيانات ناقصة"}), 400

    success, response_data = send_text_message(phone, message)
    return jsonify({"success": success, "meta_response": response_data}), 200 if success else 500


# =============================================================================
# 6. OTHER TABS (Logs & Settings)
# =============================================================================

@whatsapp_bp.route('/logs')
def logs_dashboard():
    logs = db.session.query(WhatsAppMessageLog).order_by(WhatsAppMessageLog.id.desc()).limit(150).all()
    return render_template('admin/whatsapp_dashboard.html', active_tab='logs', logs=logs)


@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_dashboard():
    access_token = current_app.config.get('WHATSAPP_ACCESS_TOKEN', '') or os.environ.get('WHATSAPP_ACCESS_TOKEN', '')
    phone_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID', '') or os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')
    
    is_connected = bool(access_token and phone_id)

    if request.method == 'POST':
        phone_number_id = request.form.get('phone_number_id')
        business_account_id = request.form.get('business_account_id')
        whatsapp_phone_number = request.form.get('whatsapp_phone_number')
        api_version = request.form.get('api_version')
        access_token_val = request.form.get('access_token')

        if phone_number_id:
            current_app.config['WHATSAPP_PHONE_NUMBER_ID'] = phone_number_id
        if business_account_id:
            current_app.config['WHATSAPP_BUSINESS_ACCOUNT_ID'] = business_account_id
        if whatsapp_phone_number:
            current_app.config['WHATSAPP_PHONE_NUMBER'] = whatsapp_phone_number
        if api_version:
            current_app.config['WHATSAPP_API_VERSION'] = api_version
        if access_token_val:
            current_app.config['WHATSAPP_ACCESS_TOKEN'] = access_token_val

        flash("✅ تم حفظ إعدادات الربط وتحديث الحالة بنجاح!", "success")
        return redirect(url_for('whatsapp_service.settings_dashboard'))

    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='settings',
        is_connected=is_connected
    )


@whatsapp_bp.route('/ping')
def ping():
    return jsonify({"status": "active", "service": "WhatsApp Service", "version": "1.0", "platform": "محجوب أونلاين"})
