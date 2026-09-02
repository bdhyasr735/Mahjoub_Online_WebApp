# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/routes.py
"""
سوق محجوب أونلاين - مسارات الباك إند والـ Webhooks
Flask / Python Routes for Meta WhatsApp Cloud API v26.0
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from datetime import datetime

# ✅ استيراد النماذج (ضروري للدوال المتعلقة بجهات الاتصال)
try:
    from apps.models.whatsapp_models import WhatsAppCustomerContact
    from apps.models.supplier_db import Supplier
    from apps.models.marketer_db import Marketer
except ImportError:
    WhatsAppCustomerContact = Supplier = Marketer = None

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


# =========================================================================
# 1. مسارات الـ Webhook مع Meta Cloud API v26.0 (تدعم كلا المسارين)
# =========================================================================

def _handle_verify():
    """التحقق الأولي من الـ Webhook من خوادم Meta (Challenge Verification)"""
    # استيراد الخدمة هنا لتفادي Circular Import
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    # إذا تم إرسال الـ Challenge الصحيح من ميتا
    if mode == 'subscribe' and token == wa_service.verify_token:
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
    # استيراد الخدمة هنا لتفادي Circular Import
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    raw_payload = request.get_data()
    signature = request.headers.get('X-Hub-Signature-256', '')
    
    if not wa_service.verify_webhook_signature(raw_payload, signature):
        return jsonify({"error": "Invalid signature"}), 401

    data = request.get_json(silent=True) or {}
    wa_service.process_incoming_payload(data)
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
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    recipient_phone = data.get('recipient_phone')
    text = data.get('content')
    
    if not recipient_phone or not text:
        return jsonify({"error": "recipient_phone and content are required"}), 400
        
    result = wa_service.send_message(recipient_phone, text)
    return jsonify(result), 200

@whatsapp_bp.route('/api/templates/send', methods=['POST'])
def send_template_api():
    """إرسال قالب رسمي معتمد (تأكيد طلب، شحنة، فاتورة)"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    recipient_phone = data.get('recipient_phone')
    template_name = data.get('template_name')
    language_code = data.get('language_code', 'ar')
    components = data.get('components', [])
    
    if not recipient_phone or not template_name:
        return jsonify({"error": "recipient_phone and template_name are required"}), 400
        
    result = wa_service.send_template(
        recipient_phone=recipient_phone,
        template_name=template_name,
        language_code=language_code,
        components=components
    )
    return jsonify(result), 200

@whatsapp_bp.route('/api/contacts', methods=['GET'])
def get_contacts():
    """جلب قائمة جهات الاتصال المسجلة في النظام"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    contacts = wa_service.get_all_contacts()
    return jsonify({"contacts": contacts}), 200

@whatsapp_bp.route('/api/messages', methods=['GET'])
def get_messages():
    """جلب الرسائل السابقة لمحادثة معينة عبر رقم الهاتف"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    phone = request.args.get('phone', '')
    if not phone:
        return jsonify({"error": "phone parameter is required"}), 400
    messages = wa_service.get_chat_history(phone)
    return jsonify({"messages": messages}), 200

@whatsapp_bp.route('/api/contacts/update-name', methods=['POST'])
def update_contact_name_api():
    """تعديل اسم جهة اتصال معينة"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    phone = data.get('phone', '')
    name = data.get('name', '')
    
    if not phone or not name:
        return jsonify({"error": "phone and name are required"}), 400
        
    result = wa_service.update_contact_name(phone, name)
    return jsonify(result), 200

@whatsapp_bp.route('/api/contacts/read', methods=['POST'])
def mark_contact_as_read_api():
    """تصفير عداد الرسائل غير المقروءة عند فتح المحادثة"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    phone = data.get('phone', '')
    
    if not phone:
        return jsonify({"error": "phone is required"}), 400
        
    result = wa_service.mark_contact_as_read(phone)
    return jsonify(result), 200

@whatsapp_bp.route('/api/send-media', methods=['POST'])
def send_media_api():
    """إرسال صور، فيديو، أو ملفات عبر Meta WhatsApp Cloud API"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    recipient_phone = request.form.get('recipient_phone', '')
    files = request.files.getlist('files')
    
    if not recipient_phone or not files:
        return jsonify({"error": "recipient_phone and files are required"}), 400
        
    result = wa_service.send_media(recipient_phone, files)
    return jsonify(result), 200

@whatsapp_bp.route('/api/clear-demo-data', methods=['POST'])
def clear_demo_data_api():
    """تطهير السجلات وحذف البيانات الوهمية من قاعدة البيانات"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    result = wa_service.clear_demo_data()
    return jsonify(result), 200


# =========================================================================
# 3. مسارات صفحات الإدارة بأسماء قوالب مميزة وفريدة
# =========================================================================

@whatsapp_bp.route('/dashboard', methods=['GET'])
@whatsapp_bp.route('/', methods=['GET'])
def dashboard_view():
    """عرض لوحة المحادثات المباشرة باستخدام القالب المخصص whatsapp_dashboard.html"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    contacts = wa_service.get_all_contacts()
    return render_template('admin/whatsapp_dashboard.html', contacts=contacts)

@whatsapp_bp.route('/templates', methods=['GET'])
def templates_view():
    """عرض قائمة قوالب Meta المعتمدة"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    templates = wa_service.get_approved_templates()
    return render_template('admin/templates_list.html', templates=templates)

@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_view():
    """عرض وتحديث مفاتيح وإعدادات Meta Cloud API"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    if request.method == 'POST':
        data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
        wa_service.update_config(data)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({"status": "success", "message": "تم حفظ الإعدادات بنجاح"}), 200
        
        config = wa_service.get_current_config()
        return render_template('admin/settings.html', config=config, success=True)

    config = wa_service.get_current_config()
    return render_template('admin/settings.html', config=config)

@whatsapp_bp.route('/webhook-logs', methods=['GET'])
def webhook_logs_view():
    """عرض سجل تدفق أحداث الـ Webhook المباشر"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    logs = wa_service.get_webhook_logs()
    return render_template('admin/webhook_logs.html', logs=logs)


# =========================================================================
# 4. 🆕 مسارات جهات الاتصال والإرسال الجماعي (مضاف حديثاً)
# =========================================================================

@whatsapp_bp.route('/contacts-bulk', methods=['GET'])
def contacts_bulk_view():
    """عرض صفحة جهات الاتصال والإرسال الجماعي (مطابقة للصور من Gemini)"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    # جلب البيانات من قاعدة البيانات
    contacts = wa_service.get_all_contacts()
    
    # إحصائيات للعرض
    stats = {
        'customers_count': 124,   # يمكن استبدالها بعدد العملاء الحقيقي
        'merchants_count': 48,
        'suppliers_count': 32,
        'marketers_count': 55
    }
    
    current_category = request.args.get('category', 'all')
    
    return render_template('admin/contacts_bulk.html', 
                           contacts=contacts, 
                           stats=stats,
                           current_category=current_category)


@whatsapp_bp.route('/add-contact', methods=['POST'])
def add_contact_view():
    """إضافة جهة اتصال جديدة"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    data = request.form.to_dict()
    result = wa_service.add_contact(
        name=data.get('name', ''),
        phone=data.get('phone', ''),
        category=data.get('category', 'customers'),
        company=data.get('company', ''),
        city=data.get('city', ''),
        email=data.get('email', ''),
        notes=data.get('notes', '')
    )
    
    if result.get('success'):
        flash('تمت إضافة جهة الاتصال بنجاح!', 'success')
    else:
        flash(result.get('error', 'حدث خطأ أثناء الإضافة'), 'danger')
        
    return redirect(url_for('whatsapp_service.contacts_bulk_view'))


@whatsapp_bp.route('/import-contacts', methods=['POST'])
def import_contacts_view():
    """استيراد جهات اتصال من ملف CSV أو Excel"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    file = request.files.get('file')
    default_category = request.form.get('default_category', 'customers')
    
    if not file:
        flash('يرجى رفع ملف أولاً', 'danger')
        return redirect(url_for('whatsapp_service.contacts_bulk_view'))
    
    try:
        import csv
        import io
        stream = io.StringIO(file.read().decode("UTF-8"))
        reader = csv.DictReader(stream)
        
        imported_count = 0
        for row in reader:
            name = row.get('Name') or row.get('name')
            phone = row.get('Phone') or row.get('phone')
            category = row.get('Category', default_category)
            
            if name and phone:
                wa_service.add_contact(name=name, phone=phone, category=category)
                imported_count += 1
        
        flash(f'تم استيراد {imported_count} جهة اتصال بنجاح!', 'success')
    except Exception as e:
        flash(f'خطأ في الاستيراد: {str(e)}', 'danger')
        
    return redirect(url_for('whatsapp_service.contacts_bulk_view'))


@whatsapp_bp.route('/send-broadcast', methods=['POST'])
def send_broadcast_view():
    """إرسال رسالة جماعية مستهدفة"""
    from apps.whatsapp_service.service import WhatsAppService
    wa_service = WhatsAppService()
    
    campaign_name = request.form.get('campaign_name', '')
    target_category = request.form.get('target_category', 'all')
    message_text = request.form.get('message_text', '')
    
    # جلب قائمة الأرقام المستهدفة
    target_phones = []
    
    if target_category == 'all' or target_category == 'customers':
        if WhatsAppCustomerContact:
            customers = WhatsAppCustomerContact.query.all()
            target_phones.extend([c.phone for c in customers])
    
    if target_category == 'all' or target_category == 'suppliers':
        if Supplier:
            suppliers = Supplier.query.all()
            target_phones.extend([s.phone for s in suppliers if s.phone])
    
    if target_category == 'all' or target_category == 'marketers':
        if Marketer:
            marketers = Marketer.query.all()
            target_phones.extend([m.phone for m in marketers if m.phone])
    
    sent_count = 0
    for phone in target_phones:
        personalized_message = message_text.replace("{phone}", phone)
        result = wa_service.send_message(recipient_phone=phone, text=personalized_message)
        if result.get('status') in ['sent', 'simulated']:
            sent_count += 1
    
    flash(f'تم إرسال الحملة بنجاح إلى {sent_count} جهة اتصال!', 'success')
    return redirect(url_for('whatsapp_service.contacts_bulk_view'))
