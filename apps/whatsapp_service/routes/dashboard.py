# coding: utf-8
# 📂 apps/whatsapp_service/dashboard.py

"""
WhatsApp Service Dashboard & UI Routes Module for Mahjoub Online WebApp
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from apps.extensions import db
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog

whatsapp_bp = Blueprint(
    'whatsapp_service',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@whatsapp_bp.route('/chat', methods=['GET'])
def chat_dashboard():
    """لوحة المحادثات المباشرة والرئيسية للواتساب"""
    try:
        contacts = WhatsAppCustomerContact.query.order_by(WhatsAppCustomerContact.last_timestamp.desc()).all()
        
        # اختيار أول عميل افتراضياً إذا لم يتم تحديد عميل
        contact_id = request.args.get('contact_id', type=int)
        current_contact = None
        messages = []
        
        if contact_id:
            current_contact = WhatsAppCustomerContact.query.get(contact_id)
        elif contacts:
            current_contact = contacts[0]
            
        if current_contact:
            messages = WhatsAppMessageLog.query.filter(
                (WhatsAppMessageLog.sender_number == current_contact.phone) | 
                (WhatsAppMessageLog.recipient_number == current_contact.phone)
            ).order_by(WhatsAppMessageLog.timestamp.asc()).all()

        return render_template(
            'admin/whatsapp_dashboard.html',
            active_tab='chat',
            contacts=contacts,
            current_contact=current_contact,
            messages=messages
        )
    except Exception as e:
        print(f"⚠️ [Chat Dashboard Error]: {e}")
        return render_template('admin/whatsapp_dashboard.html', active_tab='chat', contacts=[], current_contact=None, messages=[])


@whatsapp_bp.route('/logs', methods=['GET'])
def logs_dashboard():
    """لوحة سجل الرسائل والـ Logs"""
    try:
        logs = WhatsAppMessageLog.query.order_by(WhatsAppMessageLog.timestamp.desc()).limit(100).all()
        return render_template(
            'admin/whatsapp_dashboard.html',
            active_tab='logs',
            logs=logs
        )
    except Exception as e:
        print(f"⚠️ [Logs Dashboard Error]: {e}")
        return render_template('admin/whatsapp_dashboard.html', active_tab='logs', logs=[])


@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_dashboard():
    """لوحة إعدادات Meta WhatsApp API"""
    is_connected = True  # يمكنك ربطها بالتحقق من وجود المفاتيح في قاعدة البيانات أو الإعدادات العامة
    
    if request.method == 'POST':
        phone_number_id = request.form.get('phone_number_id')
        business_account_id = request.form.get('business_account_id')
        access_token = request.form.get('access_token')
        
        # هنا يمكنك إضافة كود حفظ الإعدادات في جدول إعدادات النظام
        flash("تم حفظ إعدادات Meta API بنجاح", "success")
        return redirect(url_for('whatsapp_service.settings_dashboard'))
        
    return render_template(
        'admin/whatsapp_dashboard.html',
        active_tab='settings',
        is_connected=is_connected
    )


# --- مسارات الـ Partials الخاصة بـ HTMX لتحديث الأجزاء ديناميكياً ---

@whatsapp_bp.route('/partials/contacts', methods=['GET'])
def partials_contacts():
    """تحديث قائمة المحادثات الجانبية تلقائياً"""
    contacts = WhatsAppCustomerContact.query.order_by(WhatsAppCustomerContact.last_timestamp.desc()).all()
    current_contact_id = request.args.get('contact_id', type=int)
    current_contact = WhatsAppCustomerContact.query.get(current_contact_id) if current_contact_id else (contacts[0] if contacts else None)
    
    # إرجاع القائمة الجانبية فقط أو القالب المخصص للـ contacts
    return render_template(
        'admin/partials/contacts_list.html', 
        contacts=contacts, 
        current_contact=current_contact
    ) if False else render_template('admin/whatsapp_dashboard.html', active_tab='chat', contacts=contacts, current_contact=current_contact, messages=[])


@whatsapp_bp.route('/partials/chat-window', methods=['GET'])
def partials_chat_window():
    """جلب صندوق المحادثة والرسائل لعميل معين عند النقر عليه"""
    contact_id = request.args.get('contact_id', type=int)
    current_contact = WhatsAppCustomerContact.query.get_or_404(contact_id)
    
    messages = WhatsAppMessageLog.query.filter(
        (WhatsAppMessageLog.sender_number == current_contact.phone) | 
        (WhatsAppMessageLog.recipient_number == current_contact.phone)
    ).order_by(WhatsAppMessageLog.timestamp.asc()).all()
    
    # تحديث حالة قراءة الرسائل إن وجد
    current_contact.unread_count = 0
    db.session.commit()

    return render_template(
        'admin/partials/chat_window_content.html',
        current_contact=current_contact,
        messages=messages
    )


@whatsapp_bp.route('/partials/client-details', methods=['GET'])
def partials_client_details():
    """جلب تفاصيل العميل الجانبية اليسرى"""
    contact_id = request.args.get('contact_id', type=int)
    current_contact = WhatsAppCustomerContact.query.get(contact_id) if contact_id else None
    
    return render_template(
        'admin/partials/client_details.html',
        current_contact=current_contact
    )


@whatsapp_bp.route('/send-message', methods=['POST'])
def send_message_htmx():
    """إرسال رسالة جديدة للعميل عبر واجهة HTMX"""
    contact_id = request.form.get('contact_id')
    phone = request.form.get('phone')
    message_content = request.form.get('message')
    
    if not message_content or not phone:
        return jsonify({"error": "Missing data"}), 400
        
    try:
        # هنا يتم استدعاء دالة الإرسال عبر Meta Cloud API الفعلية لديك
        # from apps.whatsapp_service.api import send_whatsapp_text_message
        # send_whatsapp_text_message(phone, message_content)
        
        # حفظ الرسالة في السجلات كـ outbound
        new_log = WhatsAppMessageLog(
            sender_number="system",
            recipient_number=phone,
            content=message_content,
            direction="outbound",
            message_type="text",
            status="sent"
        )
        db.session.add(new_log)
        db.session.commit()
        
        # إرجاع عنصر الرسالة الجديدة لعرضه مباشرة في الشات
        return f"""
        <div class="flex flex-col items-end">
          <div class="max-w-[65%] bg-[#f3e8ff] rounded-2xl px-4 py-3 shadow-xs border border-purple-100 text-slate-800">
            <p class="text-xs leading-relaxed">{message_content}</p>
            <div class="flex items-center justify-end gap-1 mt-1 text-[10px] text-slate-400">
              <span>الآن</span>
              <i class="fa-solid fa-check-double text-purple-600 text-[9px]"></i>
            </div>
          </div>
        </div>
        """
    except Exception as e:
        print(f"❌ [Send Message Error]: {e}")
        return f"<div class='text-red-500 text-xs'>فشل إرسال الرسالة: {e}</div>", 500
