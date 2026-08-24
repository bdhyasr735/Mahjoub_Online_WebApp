# coding: utf-8
"""
WhatsApp Dashboard Routes
Handles rendering the admin chat dashboard, contact lists, and settings views.
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from . import whatsapp_bp
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog
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
            
        # التحقق مما إذا كان العميل موجوداً مسبقاً
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
        return render_template('admin/whatsapp_dashboard.html', active_tab='settings')
    except Exception as e:
        flash(f"حدث خطأ أثناء تحميل صفحة الإعدادات: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))
