# apps/whatsapp_service/routes.py
"""
سوق محجوب أونلاين - مسارات الباك إند والـ Webhooks
Flask / Python Routes for Meta WhatsApp Cloud API v26.0
"""

from flask import Blueprint, request, jsonify, render_template
from .service import WhatsAppService

# تعريف الـ Blueprint الخاص بخدمة الواتساب
# ✅ أضفنا url_prefix='/admin/whatsapp' حتى لا يتعارض مع لوحة التحكم المركزية
whatsapp_bp = Blueprint('whatsapp', __name__, template_folder='templates', url_prefix='/admin/whatsapp')
whatsapp_service = WhatsAppService()

# =========================================================================
# 1. مسارات الـ Webhook مع Meta Cloud API v26.0
# =========================================================================

@whatsapp_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    التحقق الأولي من الـ Webhook مع خوادم Meta Graph API (Verification Challenge)
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == whatsapp_service.verify_token:
        return challenge, 200
    return "Verification failed", 403

@whatsapp_bp.route('/webhook', methods=['POST'])
def handle_webhook_event():
    """
    استقبال الرسائل وأحداث التسليم والقراءة اللحظية من Meta
    """
    raw_payload = request.get_data()
    signature = request.headers.get('X-Hub-Signature-256', '')

    # التحقق الأمني من توقيع Meta (HMAC-SHA256)
    if not whatsapp_service.verify_webhook_signature(raw_payload, signature):
        return jsonify({"error": "Invalid signature"}), 401

    data = request.get_json() or {}
    whatsapp_service.process_incoming_payload(data)
    return jsonify({"status": "received"}), 200


# =========================================================================
# 2. مسارات الـ REST API لإدارة المراسلات من لوحة التحكم
# =========================================================================

@whatsapp_bp.route('/api/send', methods=['POST'])
def send_message_api():
    """إرسال رسالة نصية مباشرة إلى هاتف العميل أو التاجر"""
    data = request.get_json() or {}
    recipient_phone = data.get('recipient_phone')
    text = data.get('content')
    
    if not recipient_phone or not text:
        return jsonify({"error": "recipient_phone and content are required"}), 400
        
    result = whatsapp_service.send_message(recipient_phone, text)
    return jsonify(result), 200

@whatsapp_bp.route('/api/templates/send', methods=['POST'])
def send_template_api():
    """إرسال قالب رسمي معتمد (تأكيد طلب، شحنة، فاتورة)"""
    data = request.get_json() or {}
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


# =========================================================================
# 3. مسارات عرض قوالب صفحات الإدارة (HTML Views)
# =========================================================================

@whatsapp_bp.route('/dashboard', methods=['GET'])
def admin_dashboard():
    """عرض لوحة المحادثات الرئيسية المجهزة بالبنفسجي الملكي"""
    contacts = whatsapp_service.get_all_contacts()
    return render_template('admin/dashboard.html', contacts=contacts)

@whatsapp_bp.route('/templates', methods=['GET'])
def admin_templates():
    """عرض قائمة قوالب Meta المعتمدة"""
    templates = whatsapp_service.get_approved_templates()
    return render_template('admin/templates_list.html', templates=templates)

@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def admin_settings():
    """عرض وتحديث مفاتيح وإعدادات Meta Cloud API"""
    if request.method == 'POST':
        whatsapp_service.update_config(request.form.to_dict())
    config = whatsapp_service.get_current_config()
    return render_template('admin/settings.html', config=config)

@whatsapp_bp.route('/webhook-logs', methods=['GET'])
def admin_webhook_logs():
    """عرض سجل تدفق أحداث الـ Webhook المباشر"""
    logs = whatsapp_service.get_webhook_logs()
    return render_template('admin/webhook_logs.html', logs=logs)
