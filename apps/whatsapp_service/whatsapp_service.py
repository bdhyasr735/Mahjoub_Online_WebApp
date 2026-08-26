import requests
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for

whatsapp_service = Blueprint('whatsapp_service', __name__, template_folder='templates')

# --- النماذج المفترضة لقاعدة البيانات (تأكد من مطابقتها لنظامك) ---
# سيتم استخدام النماذج التالية: WhatsAppMessage, WhatsAppContact, WhatsAppSetting, WhatsAppLog
# -----------------------------------------------------------------

@whatsapp_service.route('/whatsapp/dashboard', methods=['GET'])
def chat_dashboard():
    """عرض لوحة التحكم الرئيسية للمحادثات والسجلات والإعدادات"""
    active_tab = request.args.get('tab', 'chat')
    selected_phone = request.args.get('phone')
    
    # 1. جلب جهات الاتصال من قاعدة البيانات مع آخر رسالة وحالة عدم القراءة
    # (مثال: contacts = WhatsAppContact.query.order_by(WhatsAppContact.last_timestamp.desc()).all())
    contacts = [] # استبدل استعلام قاعدة البيانات هنا
    
    selected_contact = None
    messages = []
    
    if selected_phone:
        # جلب تفاصيل العميل المحدد
        # selected_contact = WhatsAppContact.query.filter_by(phone=selected_phone).first()
        # جلب رسائل المحادثة للرقم المحدد مرتبة زمنياً
        # messages = WhatsAppMessage.query.filter_by(phone=selected_phone).order_by(WhatsAppMessage.timestamp.asc()).all()
        pass

    # إذا كان التبويب هو السجلات
    logs = []
    total_logs = 0
    if active_tab == 'logs':
        # logs = WhatsAppLog.query.order_by(WhatsAppLog.timestamp.desc()).limit(50).all()
        pass

    # إذا كان التبويب هو الإعدادات
    settings = {}
    if active_tab == 'settings':
        # settings = WhatsAppSetting.get_settings()
        pass

    return render_template(
        'whatsapp_dashboard.html',
        active_tab=active_tab,
        contacts=contacts,
        selected_phone=selected_phone,
        selected_contact=selected_contact,
        messages=messages,
        logs=logs,
        total_logs=total_logs,
        settings=settings
    )


@whatsapp_service.route('/whatsapp/send-htmx', methods=['POST'])
def send_message_htmx():
    """معالجة إرسال الرسالة عبر واجهة HTMX وإعادتها فوراً للواجهة"""
    phone = request.form.get('phone')
    message_content = request.form.get('message')
    
    if not phone or not message_content:
        return "", 400

    # 1. جلب إعدادات واتساب والتوكن من النظام
    # settings = WhatsAppSetting.get_settings()
    # access_token = settings.access_token
    # phone_number_id = settings.phone_number_id
    # api_version = settings.api_version
    
    # 2. إرسال الرسالة فعلياً عبر Mah Cloud API (WhatsApp Cloud API)
    # url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    # headers = {
    #     "Authorization": f"Bearer {access_token}",
    #     "Content-Type": "application/json"
    # }
    # payload = {
    #     "messaging_product": "whatsapp",
    #     "to": phone,
    #     "type": "text",
    #     "text": {"body": message_content}
    # }
    # response = requests.post(url, json=payload, headers=headers)
    # response_data = response.json()
    # wamid = response_data.get('messages', [{}])[0].get('id', 'local_wamid')

    # 3. حفظ الرسالة الصادرة في قاعدة البيانات
    # new_msg = WhatsAppMessage(phone=phone, content=message_content, direction='outbound', status='sent', wamid=wamid, timestamp=datetime.utcnow())
    # db.session.add(new_msg)
    # db.session.commit()

    current_time_str = datetime.now().strftime('%H:%M')

    # إرجاع كود HTML الخاص بالفقرة الصادرة ليتم حقنها فوراً في شاشة الدردشة
    return f"""
    <div class="flex justify-end animate-fadeIn">
        <div class="max-w-[75%] bg-[#570575] border royal-border rounded-2xl px-4 py-2.5 shadow-md text-xs text-white relative">
            <p class="whitespace-pre-wrap leading-relaxed pb-3">{message_content}</p>
            <div class="absolute bottom-1.5 left-3 flex items-center gap-1">
                <span class="text-[9px] text-purple-200">{current_time_str}</span>
                <span class="text-[10px] font-bold text-[#D4AF37]">✓</span>
            </div>
        </div>
    </div>
    """


@whatsapp_service.route('/whatsapp/start-chat', methods=['POST'])
def start_new_chat():
    """إضافة أو فتح محادثة جديدة لرقم هاتف"""
    phone = request.form.get('phone')
    name = request.form.get('name') or phone
    
    if not phone:
        return jsonify({"success": False, "error": "رقم الهاتف مطلوب"}), 400

    # التحقق من وجود العميل مسبقاً أو إضافته
    # contact = WhatsAppContact.query.filter_by(phone=phone).first()
    # if not contact:
    #     contact = WhatsAppContact(phone=phone, name=name, created_at=datetime.utcnow())
    #     db.session.add(contact)
    # else:
    #     contact.name = name
    # db.session.commit()

    return jsonify({"success": True, "phone": phone})


@whatsapp_service.route('/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    """مسار الويب هوك (Webhook) لاستقبال رسائل الواتساب الواردة وحالات الإرسال"""
    
    # التحقق من الويب هوك (Verify Token للربط مع ميتا/Mah Cloud)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # استبدل 'YOUR_VERIFY_TOKEN' برمز التحقق الخاص بك أو جلبه من الإعدادات
        verify_token = "YOUR_VERIFY_TOKEN" 
        
        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                return challenge, 200
            else:
                return "Verification failed", 403
        return "Hello WhatsApp Webhook", 200

    # استقبال الرسائل والتحديثات الواردة (POST)
    if request.method == 'POST':
        data = request.json
        
        try:
            # التحقق من بنية رسائل الواتساب القياسية
            entry = data.get('entry', [])
            for ent in entry:
                changes = ent.get('changes', [])
                for change in changes:
                    value = change.get('value', {})
                    
                    # 1. معالجة الرسائل الواردة من العملاء
                    messages = value.get('messages', [])
                    for msg in messages:
                        sender_phone = msg.get('from') # رقم المرسل
                        msg_body = msg.get('text', {}).get('body', '') # نص الرسالة
                        wamid = msg.get('id') # معرف الرسالة من واتساب
                        
                        # قم بحفظ الرسالة في قاعدة البيانات هنا كرسالة واردة (inbound)
                        # inbound_msg = WhatsAppMessage(phone=sender_phone, content=msg_body, direction='inbound', status='received', wamid=wamid, timestamp=datetime.utcnow())
                        # db.session.add(inbound_msg)
                        # db.session.commit()

                    # 2. معالجة حالات الرسائل (تم التسليم Delivered أو تمت القراءة Read)
                    statuses = value.get('statuses', [])
                    for status in statuses:
                        wamid = status.get('id')
                        status_type = status.get('status') # sent, delivered, read
                        
                        # قم بتحديث حالة الرسالة في قاعدة البيانات بناءً على الـ wamid
                        # msg_record = WhatsAppMessage.query.filter_by(wamid=wamid).first()
                        # if msg_record:
                        #     msg_record.status = status_type
                        #     db.session.commit()

        except Exception as e:
            print(f"Error processing webhook: {e}")

        return jsonify({"status": "success"}), 200


@whatsapp_service.route('/whatsapp/settings', methods=['POST'])
def settings_view():
    """حفظ إعدادات الربط وتوكن الواتساب"""
    phone_number_id = request.form.get('whatsapp_phone_number_id')
    business_account_id = request.form.get('whatsapp_business_account_id')
    api_version = request.form.get('whatsapp_api_version')
    verify_token = request.form.get('whatsapp_verify_token')
    access_token = request.form.get('whatsapp_token')

    # حفظ القيم في جدول الإعدادات بقاعدة البيانات
    # WhatsAppSetting.update_settings(...)

    return redirect(url_for('whatsapp_service.chat_dashboard', tab='settings'))
