# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/routes.py
"""
سوق محجوب أونلاين - مسارات الباك إند والـ Webhooks
Flask / Python Routes for Meta WhatsApp Cloud API v26.0
"""

from flask import Blueprint, request, jsonify, render_template, current_app
import logging
import traceback
import os

logger = logging.getLogger(__name__)

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
    try:
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
    except Exception as e:
        logger.error(f"خطأ في التحقق من Webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

def _handle_incoming_event():
    """استقبال أحداث ورسائل Meta Webhook ومعالجتها فورياً"""
    try:
        from apps.whatsapp_service.service import WhatsAppService
        wa_service = WhatsAppService()
        
        raw_payload = request.get_data()
        signature = request.headers.get('X-Hub-Signature-256', '')
        
        # ✅ تأكد من وجود verify_token
        if hasattr(wa_service, 'verify_token') and wa_service.verify_token:
            if not wa_service.verify_webhook_signature(raw_payload, signature):
                logger.warning("توقيع Webhook غير صالح")
                return jsonify({"error": "Invalid signature"}), 401

        data = request.get_json(silent=True) or {}
        
        # ✅ معالجة البيانات الواردة
        if hasattr(wa_service, 'process_incoming_payload'):
            wa_service.process_incoming_payload(data)
        else:
            logger.warning("process_incoming_payload غير موجود في الخدمة")
        
        return jsonify({"status": "received"}), 200
    except Exception as e:
        logger.error(f"خطأ في معالجة حدث Webhook: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


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
    try:
        from apps.whatsapp_service.service import WhatsAppService
        wa_service = WhatsAppService()
        
        data = request.get_json(silent=True) or request.form.to_dict() or {}
        recipient_phone = data.get('recipient_phone') or data.get('phone')
        text = data.get('content') or data.get('text')
        
        if not recipient_phone or not text:
            return jsonify({"error": "recipient_phone and content are required"}), 400
            
        result = wa_service.send_message(recipient_phone, text)
        return jsonify({"success": True, "result": result}), 200
    except Exception as e:
        logger.error(f"خطأ في إرسال الرسالة: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@whatsapp_bp.route('/api/templates/send', methods=['POST'])
def send_template_api():
    """إرسال قالب رسمي معتمد (تأكيد طلب، شحنة، فاتورة)"""
    try:
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
        return jsonify({"success": True, "result": result}), 200
    except Exception as e:
        logger.error(f"خطأ في إرسال القالب: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@whatsapp_bp.route('/api/contacts', methods=['GET'])
def get_contacts():
    """جلب قائمة جهات الاتصال المسجلة في النظام"""
    try:
        from apps.whatsapp_service.service import WhatsAppService
        wa_service = WhatsAppService()
        
        contacts = wa_service.get_all_contacts()
        return jsonify({"contacts": contacts, "count": len(contacts)}), 200
    except Exception as e:
        logger.error(f"خطأ في جلب جهات الاتصال: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e), "contacts": []}), 500

@whatsapp_bp.route('/api/messages', methods=['GET'])
def get_messages():
    """جلب الرسائل السابقة لمحادثة معينة عبر رقم الهاتف"""
    try:
        from apps.whatsapp_service.service import WhatsAppService
        wa_service = WhatsAppService()
        
        phone = request.args.get('phone', '')
        if not phone:
            return jsonify({"error": "phone parameter is required"}), 400
        messages = wa_service.get_chat_history(phone)
        return jsonify({"messages": messages, "count": len(messages)}), 200
    except Exception as e:
        logger.error(f"خطأ في جلب الرسائل: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e), "messages": []}), 500

@whatsapp_bp.route('/api/messages/<phone>', methods=['GET'])
def get_messages_by_phone(phone):
    """جلب الرسائل السابقة لمحادثة معينة (بديل)"""
    try:
        from apps.whatsapp_service.service import WhatsAppService
        wa_service = WhatsAppService()
        
        messages = wa_service.get_chat_history(phone)
        return jsonify({"messages": messages, "count": len(messages)}), 200
    except Exception as e:
        logger.error(f"خطأ في جلب الرسائل: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e), "messages": []}), 500

@whatsapp_bp.route('/api/contacts/update-name', methods=['POST'])
def update_contact_name_api():
    """تعديل اسم جهة اتصال معينة"""
    try:
        from apps.whatsapp_service.service import WhatsAppService
        wa_service = WhatsAppService()
        
        data = request.get_json(silent=True) or request.form.to_dict() or {}
        phone = data.get('phone', '')
        name = data.get('name', '')
        
        if not phone or not name:
            return jsonify({"error": "phone and name are required"}), 400
            
        result = wa_service.update_contact_name(phone, name)
        return jsonify({"success": True, "result": result}), 200
    except Exception as e:
        logger.error(f"خطأ في تحديث الاسم: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@whatsapp_bp.route('/api/contacts/read', methods=['POST'])
def mark_contact_as_read_api():
    """تصفير عداد الرسائل غير المقروءة عند فتح المحادثة"""
    try:
        from apps.whatsapp_service.service import WhatsAppService
        wa_service = WhatsAppService()
        
        data = request.get_json(silent=True) or request.form.to_dict() or {}
        phone = data.get('phone', '')
        
        if not phone:
            return jsonify({"error": "phone is required"}), 400
            
        result = wa_service.mark_contact_as_read(phone)
        return jsonify({"success": True, "result": result}), 200
    except Exception as e:
        logger.error(f"خطأ في تصفير العداد: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@whatsapp_bp.route('/api/send-media', methods=['POST'])
def send_media_api():
    """إرسال صور، فيديو، أو ملفات عبر Meta WhatsApp Cloud API"""
    try:
        from apps.whatsapp_service.service import WhatsAppService
        wa_service = WhatsAppService()
        
        recipient_phone = request.form.get('recipient_phone', '')
        files = request.files.getlist('files')
        
        if not recipient_phone or not files:
            return jsonify({"error": "recipient_phone and files are required"}), 400
            
        result = wa_service.send_media(recipient_phone, files)
        return jsonify({"success": True, "result": result}), 200
    except Exception as e:
        logger.error(f"خطأ في إرسال الميديا: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@whatsapp_bp.route('/api/clear-demo-data', methods=['POST'])
def clear_demo_data_api():
    """تطهير السجلات وحذف البيانات الوهمية من قاعدة البيانات"""
    try:
        from apps.whatsapp_service.service import WhatsAppService
        wa_service = WhatsAppService()
        
        result = wa_service.clear_demo_data()
        return jsonify({"success": True, "result": result}), 200
    except Exception as e:
        logger.error(f"خطأ في تنظيف البيانات: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# =========================================================================
# 3. مسارات صفحات الإدارة بأسماء قوالب مميزة وفريدة
# =========================================================================

@whatsapp_bp.route('/dashboard', methods=['GET'])
@whatsapp_bp.route('/', methods=['GET'])
def dashboard_view():
    """عرض لوحة المحادثات المباشرة باستخدام القالب المخصص whatsapp_dashboard.html"""
    try:
        from apps.whatsapp_service.service import WhatsAppService
        wa_service = WhatsAppService()
        
        # ✅ جلب جهات الاتصال مع رسائل غير مقروءة
        contacts = wa_service.get_all_contacts()
        
        # ✅ تأكد من أن contacts هو قائمة
        if not isinstance(contacts, list):
            contacts = []
        
        # ✅ تسجيل عدد الجهات للتصحيح
        logger.info(f"تم تحميل {len(contacts)} جهة اتصال")
        
        return render_template('admin/whatsapp_dashboard.html', contacts=contacts)
    except Exception as e:
        logger.error(f"خطأ في عرض لوحة التحكم: {str(e)}")
        logger.error(traceback.format_exc())
        
        # ✅ عرض القالب مع رسالة خطأ بدلاً من 500
        return render_template(
            'admin/whatsapp_dashboard.html',
            contacts=[],
            error=f"حدث خطأ: {str(e)}"
        ), 200  # استخدام 200 لعرض الصفحة مع الخطأ

@whatsapp_bp.route('/templates', methods=['GET'])
def templates_view():
    """عرض قائمة قوالب Meta المعتمدة"""
    try:
        from apps.whatsapp_service.service import WhatsAppService
        wa_service = WhatsAppService()
        
        templates = wa_service.get_approved_templates()
        if not isinstance(templates, list):
            templates = []
            
        return render_template('admin/templates_list.html', templates=templates)
    except Exception as e:
        logger.error(f"خطأ في عرض القوالب: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template(
            'admin/templates_list.html',
            templates=[],
            error=str(e)
        ), 200

@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_view():
    """عرض وتحديث مفاتيح وإعدادات Meta Cloud API"""
    try:
        from apps.whatsapp_service.service import WhatsAppService
        wa_service = WhatsAppService()
        
        if request.method == 'POST':
            data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
            
            # ✅ تحديث الإعدادات
            if hasattr(wa_service, 'update_config'):
                wa_service.update_config(data)
            else:
                # تحديث مباشر في البيئة
                for key, value in data.items():
                    if key in ['WHATSAPP_PHONE_NUMBER_ID', 'WHATSAPP_ACCESS_TOKEN', 
                              'WHATSAPP_API_VERSION', 'WHATSAPP_VERIFY_TOKEN']:
                        os.environ[key] = value
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                return jsonify({"status": "success", "message": "تم حفظ الإعدادات بنجاح"}), 200
            
            config = wa_service.get_current_config() if hasattr(wa_service, 'get_current_config') else {}
            return render_template('admin/settings.html', config=config, success=True)

        config = wa_service.get_current_config() if hasattr(wa_service, 'get_current_config') else {}
        return render_template('admin/settings.html', config=config)
    except Exception as e:
        logger.error(f"خطأ في الإعدادات: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template(
            'admin/settings.html',
            config={},
            error=str(e)
        ), 200

@whatsapp_bp.route('/webhook-logs', methods=['GET'])
def webhook_logs_view():
    """عرض سجل تدفق أحداث الـ Webhook المباشر"""
    try:
        from apps.whatsapp_service.service import WhatsAppService
        wa_service = WhatsAppService()
        
        logs = wa_service.get_webhook_logs() if hasattr(wa_service, 'get_webhook_logs') else []
        if not isinstance(logs, list):
            logs = []
            
        return render_template('admin/webhook_logs.html', logs=logs)
    except Exception as e:
        logger.error(f"خطأ في عرض سجل Webhook: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template(
            'admin/webhook_logs.html',
            logs=[],
            error=str(e)
        ), 200


# =========================================================================
# 4. مسار اختبار للتحقق من عمل الخدمة
# =========================================================================

@whatsapp_bp.route('/test', methods=['GET'])
def test_service():
    """مسار اختبار للتحقق من عمل الخدمة"""
    try:
        from apps.whatsapp_service.service import WhatsAppService
        wa_service = WhatsAppService()
        
        # ✅ اختبار الاتصال
        status = {
            "status": "online",
            "service": "WhatsApp Service",
            "version": "v26.0",
            "config": {
                "phone_number_id": getattr(wa_service, 'phone_number_id', 'غير محدد'),
                "api_version": getattr(wa_service, 'api_version', 'غير محدد'),
                "verify_token": "محدد" if getattr(wa_service, 'verify_token', None) else "غير محدد"
            }
        }
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
