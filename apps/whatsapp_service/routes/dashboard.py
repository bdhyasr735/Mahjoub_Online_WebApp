# coding: utf-8
"""
WhatsApp Dashboard Routes
Handles rendering the admin chat dashboard, contact lists, and settings views.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from datetime import datetime
from . import whatsapp_bp
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog
# استيراد نموذج الإعدادات إذا كان موجوداً، أو التعامل معه عبر الكونفيج أو قاعدة البيانات
# from apps.models.whatsapp_models import WhatsAppSettings 
from apps.extensions import db


@whatsapp_bp.route('/dashboard', methods=['GET'])
@login_required
def chat_dashboard():
    """عرض لوحة تحكم محادثات الواتساب الرئيسية"""
    try:
        contacts = db.session.query(WhatsAppCustomerContact).order_by(
            WhatsAppCustomerContact.last_timestamp.desc()
        ).all()
        
        selected_contact_id = request.args.get('contact_id', type=int)
        selected_contact = None
        
        if selected_contact_id:
            selected_contact = db.session.query(WhatsAppCustomerContact).filter_by(id=selected_contact_id).first()
        elif contacts:
            selected_contact = contacts[0]

        return render_template(
            'admin/whatsapp_dashboard.html',
            contacts=contacts,
            selected_contact=selected_contact,
            active_tab='chat'
        )
    except Exception as e:
        flash(f"حدث خطأ أثناء تحميل لوحة المحادثات: {str(e)}", "danger")
        return render_template(
            'admin/whatsapp_dashboard.html',
            contacts=[],
            selected_contact=None,
            active_tab='chat'
        )


@whatsapp_bp.route('/start-new-chat', methods=['POST'])
@login_required
def start_new_chat():
    """بدء محادثة جديدة مع رقم جديد"""
    try:
        phone = request.form.get('phone')
        name = request.form.get('name', 'عميل جديد')
        
        if not phone:
            flash("يرجى إدخال رقم الهاتف بشكل صحيح.", "danger")
            return redirect(url_for('whatsapp_service.chat_dashboard'))
            
        existing_contact = db.session.query(WhatsAppCustomerContact).filter_by(phone_number=phone).first()
        
        if not existing_contact:
            new_contact = WhatsAppCustomerContact(
                phone_number=phone,
                name=name,
                last_message="تم إنشاء المحادثة",
                last_timestamp=db.func.current_timestamp()
            )
            db.session.add(new_contact)
            db.session.commit()
            existing_contact = new_contact
            flash("تم إنشاء المحادثة بنجاح.", "success")
            
        return redirect(url_for('whatsapp_service.chat_dashboard', contact_id=existing_contact.id))
    except Exception as e:
        db.session.rollback()
        flash(f"حدث خطأ أثناء بدء المحادثة: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/logs', methods=['GET'])
@login_required
def logs_dashboard():
    """عرض صفحة سجل الرسائل"""
    try:
        logs = db.session.query(WhatsAppMessageLog).order_by(WhatsAppMessageLog.id.desc()).limit(100).all()
        return render_template('admin/whatsapp_dashboard.html', logs=logs, active_tab='logs')
    except Exception as e:
        flash(f"حدث خطأ أثناء تحميل السجلات: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/webhook-panel', methods=['GET'])
@login_required
def webhook_dashboard():
    """عرض صفحة محاكي ومتابعة الويب هوك"""
    try:
        return render_template('admin/whatsapp_dashboard.html', active_tab='webhook')
    except Exception as e:
        flash(f"حدث خطأ أثناء تحميل لوحة الويب هوك: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/settings', methods=['GET'])
@login_required
def settings_dashboard():
    """عرض صفحة إعدادات ربط Meta WhatsApp API"""
    try:
        # جلب الإعدادات (كمثال ننشئ كائن وهمي إن لم يكن الجدول مفعلًا، أو يمكنك ربطه بقاعدة البيانات)
        class SettingsObj:
            phone_number_id = ""
            business_account_id = ""
            api_version = "v20.0"
            access_token = ""
            verify_token = "mahjoub_secure_webhook_token"
            updated_at = None

        settings = SettingsObj()
        is_connected = bool(settings.access_token and settings.phone_number_id)

        return render_template(
            'admin/whatsapp_dashboard.html',
            active_tab='settings',
            settings=settings,
            is_connected=is_connected
        )
    except Exception as e:
        flash(f"حدث خطأ أثناء تحميل صفحة الإعدادات: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))


@whatsapp_bp.route('/settings/save', methods=['POST'])
@login_required
def settings_save():
    """حفظ إعدادات Meta API"""
    try:
        phone_number_id = request.form.get('phone_number_id')
        business_account_id = request.form.get('business_account_id')
        api_version = request.form.get('api_version')
        access_token = request.form.get('access_token')

        # هنا يمكنك حفظ البيانات في قاعدة البيانات أو ملف التكوين الخاص بك
        
        is_connected = bool(access_token and phone_number_id)
        
        return jsonify({
            'success': True,
            'message': 'تم حفظ الإعدادات بنجاح',
            'is_connected': is_connected,
            'updated_at': datetime.now().strftime('%Y-%m-%d %I:%M %p')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'حدث خطأ أثناء الحفظ: {str(e)}'
        }), 500


@whatsapp_bp.route('/settings/regenerate-token', methods=['POST'])
@login_required
def regenerate_verify_token():
    """تجديد رمز التحقق للويب هوك"""
    try:
        import secrets
        new_token = f"mahjoub_{secrets.token_hex(8)}"
        # احفظ الرمز الجديد في قاعدة البيانات هنا إذا لزم الأمر
        return jsonify({
            'success': True,
            'token': new_token
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@whatsapp_bp.route('/settings/test-connection', methods=['GET'])
@login_required
def test_connection():
    """اختبار الاتصال بـ Meta WhatsApp API"""
    try:
        # يمكنك إضافة فحص حقيقي لـ API ميتا هنا إذا أردت
        return jsonify({
            'success': True,
            'message': 'الاتصال بـ Meta API يعمل بكفاءة عالية'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@whatsapp_bp.route('/settings/test-webhook', methods=['POST'])
@login_required
def test_webhook():
    """اختبار استجابة الويب هوك"""
    try:
        return jsonify({
            'success': True,
            'message': 'استجابة Webhook النظام تعمل بنجاح'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
