# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/routes.py
"""
سوق محجوب أونلاين - مسارات الباك إند والـ Webhooks
Flask / Python Routes for Meta WhatsApp Cloud API v26.0
"""

from flask import Blueprint, request, jsonify, render_template

# دعم الاستيراد النسبي والمطلق بمرونة تامة
try:
    from .service import WhatsAppService
except ImportError:
    try:
        from apps.whatsapp_service.service import WhatsAppService
    except ImportError:
        from whatsapp_service.service import WhatsAppService

# تعريف الـ Blueprint الإداري
whatsapp_bp = Blueprint(
    'whatsapp_service', 
    __name__, 
    template_folder='templates',
    url_prefix='/admin/whatsapp'
)

# تعريف Blueprint عام لمسارات الويب هوك المباشرة بدون بادئة admin
webhook_public_bp = Blueprint(
    'whatsapp_webhook_public',
    __name__
)

whatsapp_service = WhatsAppService()

# =========================================================================
# 1. مسارات الـ Webhook مع Meta Cloud API v26.0 (تدعم كلا المسارين)
# =========================================================================

def _handle_verify():
    """التحقق الأولي من الـ Webhook من خوادم Meta (Challenge Verification)"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    # إذا تم إرسال الـ Challenge الصحيح من ميتا
    if mode == 'subscribe' and token == whatsapp_service.verify_token:
        return str(challenge), 200

    # إذا قام المطور بفتح الرابط يدوياً للتأكد من عمل السيرفر
    if not mode and not token:
        return jsonify({
            "status": "online",
            "service": "Mahjoob WhatsApp Webhook Endpoint (v26.0)",
            "message": "Webhook is running and ready to receive Meta Cloud API events."
        }), 200

    return "Verification failed: Token mismatch", 403

def _handle_incoming_event():
    """استقبال أحداث ورسائل Meta Webhook ومعالجتها فورياً"""
    raw_payload = request.get_data()
    signature = request.headers.get('X-Hub-Signature-256', '')

    if not whatsapp_service.verify_webhook_signature(raw_payload, signature):
        return jsonify({"error": "Invalid signature"}), 401

    data = request.get_json(silent=True) or {}
    whatsapp_service.process_incoming_payload(data)
    return jsonify({"status": "received"}), 200


# مسارات الويب هوك تحت /admin/whatsapp/webhook
@whatsapp_bp.route('/webhook', methods=['GET'])
def verify_webhook_admin():
    return _handle_verify()

@whatsapp_bp.route('/webhook', methods=['POST'])
def handle_webhook_event_admin():
    return _handle_incoming_event()


# مسارات الويب هوك المباشرة تحت /whatsapp/webhook (لحل الـ 404)
@webhook_public_bp.route('/whatsapp/webhook', methods=['GET'])
def verify_webhook_public():
    return _handle_verify()

@webhook_public_bp.route('/whatsapp/webhook', methods=['POST'])
def handle_webhook_event_public():
    return _handle_incoming_event()


# =========================================================================
# 2. مسارات الـ REST API لإدارة المراسلات من لوحة التحكم
# =========================================================================

@whatsapp_bp.route('/api/send', methods=['POST'])
def send_message_api():
    """إرسال رسالة نصية مباشرة إلى هاتف العميل أو التاجر"""
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    recipient_phone = data.get('recipient_phone')
    text = data.get('content')
    
    if not recipient_phone or not text:
        return jsonify({"error": "recipient_phone and content are required"}), 400
        
    result = whatsapp_service.send_message(recipient_phone, text)
    return jsonify(result), 200

@whatsapp_bp.route('/api/templates/send', methods=['POST'])
def send_template_api():
    """إرسال قالب رسمي معتمد (تأكيد طلب، شحنة، فاتورة)"""
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    recipient_phone = data.get('recipient_phone')
    template_name = data.get('template_name')
    language_code = data.get('language_code', 'ar')
    components = data.get('components', [])
    
    if not recipient_phone or not template_name:
        return jsonify({"error": "recipient_phone and template_name are required"}), 400
        
    result = whatsapp_service.send_template(
        recipient_phone=recipient_phone,
        template_name=template_name,
        language_code=language_code,
        components=components
    )
    return jsonify(result), 200

@whatsapp_bp.route('/api/contacts', methods=['GET'])
def get_contacts():
    """جلب قائمة جهات الاتصال المسجلة في النظام"""
    contacts = whatsapp_service.get_all_contacts()
    return jsonify({"contacts": contacts}), 200

@whatsapp_bp.route('/api/messages', methods=['GET'])
def get_messages():
    """جلب الرسائل السابقة لمحادثة معينة عبر رقم الهاتف"""
    phone = request.args.get('phone', '')
    if not phone:
        return jsonify({"error": "phone parameter is required"}), 400
    messages = whatsapp_service.get_chat_history(phone)
    return jsonify({"messages": messages}), 200

@whatsapp_bp.route('/api/clear-demo-data', methods=['POST'])
def clear_demo_data_api():
    """تطهير السجلات وحذف البيانات الوهمية من قاعدة البيانات"""
    result = whatsapp_service.clear_demo_data()
    return jsonify(result), 200


# =========================================================================
# 3. مسارات صفحات الإدارة بأسماء قوالب مميزة وفريدة
# =========================================================================

@whatsapp_bp.route('/dashboard', methods=['GET'])
@whatsapp_bp.route('/', methods=['GET'])
def dashboard_view():
    """عرض لوحة المحادثات المباشرة باستخدام القالب المخصص whatsapp_dashboard.html"""
    contacts = whatsapp_service.get_all_contacts()
    return render_template('admin/whatsapp_dashboard.html', contacts=contacts)

@whatsapp_bp.route('/templates', methods=['GET'])
def templates_view():
    """عرض قائمة قوالب Meta المعتمدة"""
    templates = whatsapp_service.get_approved_templates()
    return render_template('admin/templates_list.html', templates=templates)

@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_view():
    """عرض وتحديث مفاتيح وإعدادات Meta Cloud API"""
    if request.method == 'POST':
        data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
        whatsapp_service.update_config(data)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({"status": "success", "message": "تم حفظ الإعدادات بنجاح"}), 200
        
        config = whatsapp_service.get_current_config()
        return render_template('admin/settings.html', config=config, success=True)

    config = whatsapp_service.get_current_config()
    return render_template('admin/settings.html', config=config)

@whatsapp_bp.route('/webhook-logs', methods=['GET'])
def webhook_logs_view():
    """عرض سجل تدفق أحداث الـ Webhook المباشر"""
    logs = whatsapp_service.get_webhook_logs()
    return render_template('admin/webhook_logs.html', logs=logs)
