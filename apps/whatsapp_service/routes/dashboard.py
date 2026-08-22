from flask import Blueprint, render_template, request, jsonify, current_app
from sqlalchemy import or_
# تأكد من استيراد النماذج وقاعدة البيانات الخاصة بمشروعك (محجوب أونلاين)
from .models import db, WhatsAppContact, WhatsAppMessageLog

whatsapp_service = Blueprint('whatsapp_service', __name__, template_folder='templates')

@whatsapp_service.route('/dashboard/chat', methods=['GET'])
def chat_dashboard():
    """عرض لوحة التحكم الرئيسية للمحادثات المباشرة"""
    # جلب جميع جهات الاتصال مرتبة حسب آخر نشاط
    contacts = WhatsAppContact.query.order_by(WhatsAppContact.last_timestamp.desc()).all()
    
    # تحديد العميل الافتراضي (أول عميل أو بناءً على المعرف المرفق)
    contact_id = request.args.get('contact_id', type=int)
    current_contact = None
    messages = []
    
    if contact_id:
        current_contact = WhatsAppContact.query.get(contact_id)
    elif contacts:
        current_contact = contacts[0] # اختيار أول عميل تلقائياً إن لم يُحدد
        
    # جلب الرسائل الخاصة بالعميل الحالي إن وجد
    if current_contact:
        messages = WhatsAppMessageLog.query.filter(
            or_(
                WhatsAppMessageLog.sender_number == current_contact.phone,
                WhatsAppMessageLog.recipient_number == current_contact.phone
            )
        ).order_by(WhatsAppMessageLog.timestamp.asc()).all()

    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='chat',
        contacts=contacts,
        current_contact=current_contact,
        messages=messages,
        is_connected=True
    )

@whatsapp_service.route('/dashboard/logs', methods=['GET'])
def logs_dashboard():
    """عرض تبويب سجل الرسائل (Logs)"""
    logs = WhatsAppMessageLog.query.order_by(WhatsAppMessageLog.timestamp.desc()).limit(100).all()
    contacts = WhatsAppContact.query.all()
    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='logs',
        logs=logs,
        contacts=contacts
    )

@whatsapp_service.route('/dashboard/settings', methods=['GET', 'POST'])
def settings_dashboard():
    """إدارة إعدادات الربط مع Meta API"""
    if request.method == 'POST':
        phone_number_id = request.form.get('phone_number_id')
        business_account_id = request.form.get('business_account_id')
        access_token = request.form.get('access_token')
        # قم هنا بحفظ الإعدادات في قاعدة البيانات أو ملف التكوين
        # ...
    
    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='settings',
        is_connected=True
    )

# ==================== المسارات المصغرة (HTMX Partials) ====================

@whatsapp_service.route('/dashboard/partials/chat-window', methods=['GET'])
def partials_chat_window():
    """جلب نافذة المحادثة الخاصة بعميل معين عند النقر عليه أو التحديث التلقائي"""
    contact_id = request.args.get('contact_id', type=int)
    current_contact = WhatsAppContact.query.get_or_404(contact_id)
    
    messages = WhatsAppMessageLog.query.filter(
        or_(
            WhatsAppMessageLog.sender_number == current_contact.phone,
            WhatsAppMessageLog.recipient_number == current_contact.phone
        )
    ).order_by(WhatsAppMessageLog.timestamp.asc()).all()

    # نعيد إرجاع جزء نافذة المحادثة فقط (الموجود داخل chat-area-container)
    return render_template(
        'admin/partials/chat_window.html',
        current_contact=current_contact,
        messages=messages
    )

@whatsapp_service.route('/dashboard/partials/client-details', methods=['GET'])
def partials_client_details():
    """جلب لوحة تفاصيل العميل الجانبية اليسرى عبر HTMX"""
    contact_id = request.args.get('contact_id', type=int)
    current_contact = WhatsAppContact.query.get_or_404(contact_id)
    
    return render_template(
        'admin/partials/client_details.html',
        current_contact=current_contact
    )

@whatsapp_service.route('/dashboard/partials/contacts', methods=['GET'])
def partials_contacts():
    """تحديث قائمة المحادثات النشطة في الشريط الجانبي تلقائياً"""
    contacts = WhatsAppContact.query.order_by(WhatsAppContact.last_timestamp.desc()).all()
    current_contact_id = request.args.get('contact_id', type=int)
    current_contact = WhatsAppContact.query.get(current_contact_id) if current_contact_id else None
    
    return render_template(
        'admin/partials/contacts_list.html',
        contacts=contacts,
        current_contact=current_contact
    )

@whatsapp_service.route('/dashboard/send-message', methods=['POST'])
def send_message_htmx():
    """معالجة إرسال رسالة جديدة عبر النموذج وإرجاعها للقالب مباشرة"""
    contact_id = request.form.get('contact_id', type=int)
    phone = request.form.get('phone')
    message_text = request.form.get('message')
    
    # هنا يتم وضع منطق الإرسال الفعلي عبر Meta WhatsApp API وحفظها في قاعدة البيانات
    # ...
    
    # كمثال افتراضي بعد الحفظ، نقوم بإنشاء كائن رسالة صادرة مؤقت لعرضه مباشرة في الواجهة
    new_msg = WhatsAppMessageLog(
        direction='outbound',
        sender_number='966500000000', # رقم النظام
        recipient_number=phone,
        content=message_text,
        message_type='text',
        status='sent'
    )
    db.session.add(new_msg)
    db.session.commit()
    
    # إرجاع HTML الرسالة الصادرة لكي يتم إضافتها بواسطة HTMX مباشرة داخل صندوق الرسائل
    return f"""
    <div class="flex flex-col items-end">
        <div class="max-w-[65%] bg-[#f3e8ff] rounded-2xl px-4 py-3 shadow-xs border border-purple-100 text-slate-800">
            <p class="text-xs leading-relaxed">{new_msg.content}</p>
            <div class="flex items-center justify-end gap-1 mt-1 text-[10px] text-slate-400">
                <span>الآن</span>
                <i class="fa-solid fa-check-double text-purple-600 text-[9px]"></i>
            </div>
        </div>
    </div>
    """
