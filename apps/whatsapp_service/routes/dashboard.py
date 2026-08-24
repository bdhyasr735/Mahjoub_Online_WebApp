# coding: utf-8
"""
WhatsApp Dashboard Routes
Handles rendering the admin chat dashboard, contact lists, and settings views.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from . import whatsapp_bp
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog
from apps.extensions import db


@whatsapp_bp.route('/dashboard', methods=['GET'])
@login_required
def chat_dashboard():
    """عرض لوحة تحكم محادثات الواتساب الرئيسية"""
    try:
        # جلب قائمة جهات الاتصال مرتبة حسب أحدث رسالة
        contacts = db.session.query(WhatsAppCustomerContact).order_by(
            WhatsAppCustomerContact.updated_at.desc()
        ).all()
        
        # التحقق من وجود معرف جهة اتصال مطلوب في الرابط
        selected_contact_id = request.args.get('contact_id', type=int)
        selected_contact = None
        
        if selected_contact_id:
            selected_contact = db.session.query(WhatsAppCustomerContact).filter_by(id=selected_contact_id).first()
        elif contacts:
            selected_contact = contacts[0] # اختيار أول عميل افتراضياً إن لم يُحدد

        return render_template(
            'whatsapp/dashboard.html',
            contacts=contacts,
            selected_contact=selected_contact
        )
    except Exception as e:
        flash(f"حدث خطأ أثناء تحميل لوحة المحادثات: {str(e)}", "danger")
        return render_template('whatsapp/dashboard.html', contacts=[], selected_contact=None)


@whatsapp_bp.route('/settings', methods=['GET'])
@login_required
def settings_dashboard():
    """عرض صفحة إعدادات ربط Meta WhatsApp API"""
    try:
        return render_template('whatsapp/settings.html')
    except Exception as e:
        flash(f"حدث خطأ أثناء تحميل صفحة الإعدادات: {str(e)}", "danger")
        return redirect(url_for('whatsapp_service.chat_dashboard'))
