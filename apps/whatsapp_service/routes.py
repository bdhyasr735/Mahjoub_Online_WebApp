from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from datetime import datetime
import requests

# افتراض أنك تستورد نماذج البيانات وقاعدة البيانات الخاصة بك من apps.models.whatsapp_models أو ما يناسب هيكلتك
# from apps.models.whatsapp_models import db, WhatsAppContact, WhatsAppMessage, WhatsAppSettings, WhatsAppLog

whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    url_prefix='/admin/whatsapp',
    template_folder='templates'
)

@whatsapp_bp.route('/', methods=['GET', 'POST'])
def whatsapp_dashboard():
    """
    لوحة تحكم موحدة بالكامل: تدير عرض المحادثات، إرسال الرسائل، عرض السجلات،
    الويب هوك، والإعدادات من خلال تبويب واحد أو قالب مفرد (whatsapp_dashboard.html).
    """
    active_tab = request.args.get('tab', 'chat')
    contact_id = request.args.get('contact_id', type=int)
    
    # جلب الإعدادات والبيانات الأساسية (تأكد من تعديلها بحسب نماذج قاعدة البيانات لديك)
    # settings = WhatsAppSettings.query.first()
    # contacts = WhatsAppContact.query.order_by(WhatsAppContact.last_timestamp.desc()).all()
    # logs = WhatsAppLog.query.order_by(WhatsAppLog.timestamp.desc()).limit(50).all()
    
    # نموذج بيانات وهمي لتوضيح الربط المباشر بالقالب المفرد:
    settings = {"phone_number_id": "105500000000", "verify_token": "mahjoub_verify", "access_token": ""}
    contacts = []
    messages = []
    logs = []
    selected_contact = None

    if contact_id:
        # selected_contact = WhatsAppContact.query.get(contact_id)
        # messages = WhatsAppMessage.query.filter_by(contact_id=contact_id).order_by(WhatsAppMessage.timestamp.asc()).all()
        pass

    # معالجة حفظ الإعدادات إذا تم إرسالها من تبويب الإعدادات
    if request.method == 'POST' and active_tab == 'settings':
        phone_id = request.form.get('whatsapp_phone_number_id')
        token = request.form.get('whatsapp_token')
        # تحديث قاعدة البيانات...
        flash('تم حفظ الإعدادات بنجاح', 'success')
        return redirect(url_for('whatsapp_service.whatsapp_dashboard', tab='settings'))

    # معالجة إرسال رسالة جديدة عبر HTMX أو الطلب العادي
    if request.method == 'POST' and active_tab == 'chat':
        phone = request.form.get('phone')
        message_text = request.form.get('message')
        
        if message_text and phone:
            # منطق الإرسال عبر Meta Cloud API
            # response = send_whatsapp_message_api(phone, message_text, settings)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # إرجاع فقرة الرسالة الجديدة فقط لتحديث الواجهة لحظياً
                return f'''
                <div class="message-item flex justify-start animate-fadeIn">
                  <div class="max-w-[75%] bg-[#570575]/40 border border-[#570575]/50 rounded-lg px-3 py-1.5 shadow-md text-xs text-[#e9edef] relative">
                    <p class="whitespace-pre-wrap leading-relaxed pt-0.5 pb-1">{message_text}</p>
                    <div class="flex items-center justify-end gap-1 float-left ml-1 mt-[-6px]">
                      <span class="text-[9px] text-[#e9edef]/60">{datetime.now().strftime('%I:%M %p')}</span>
                      <span class="text-[10px] font-bold text-[#D4AF37]">✓✓</span>
                    </div>
                  </div>
                </div>
                '''

    return render_template(
        'admin/whatsapp/whatsapp_dashboard.html',
        active_tab=active_tab,
        settings=settings,
        contacts=contacts,
        selected_contact=selected_contact,
        messages=messages,
        logs=logs,
        today=datetime.now().strftime('%Y-%m-%d')
    )


@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
endef_webhook_handler():
    """مستقبل الويب هوك الخاص بـ Meta"""
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # تحقق من الرمز
        if mode and token:
            if token == 'mahjoub_verify': # أو جلبها من الإعدادات
                return challenge, 200
            return 'Forbidden', 403
        return 'Bad Request', 400
        
    elif request.method == 'POST':
        data = request.json
        # معالجة الرسائل الواردة وتخزينها في قاعدة البيانات
        return jsonify({"status": "success"}), 200
