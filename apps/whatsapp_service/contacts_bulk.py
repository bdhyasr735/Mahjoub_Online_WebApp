# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/contacts_bulk.py
"""
ملف مساعد (Helper) فقط - لا يحتوي على Blueprint
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from apps.extensions import db

# استيراد النماذج
from apps.models.whatsapp_models import WhatsAppCustomerContact
from apps.models.supplier_db import Supplier
from apps.models.marketer_db import Marketer

# استيراد الخدمة (المحرك)
from apps.whatsapp_service.service import WhatsAppService


# =========================================================================
# 1. عرض صفحة جهات الاتصال
# =========================================================================
@login_required
def contacts_bulk_view():
    wa_service = WhatsAppService()
    
    all_contacts = wa_service.get_all_contacts()
    
    try:
        customers_count = WhatsAppCustomerContact.query.count()
        suppliers_count = Supplier.query.count()
        marketers_count = Marketer.query.count()
        merchants_count = suppliers_count
    except Exception:
        customers_count, suppliers_count, marketers_count, merchants_count = 0, 0, 0, 0

    stats = {
        'customers_count': customers_count,
        'merchants_count': merchants_count,
        'suppliers_count': suppliers_count,
        'marketers_count': marketers_count
    }

    current_category = request.args.get('category', 'all')
    
    return render_template('admin/contacts_bulk.html', 
                           contacts=all_contacts, 
                           stats=stats,
                           current_category=current_category)


# =========================================================================
# 2. إضافة جهة اتصال جديدة
# =========================================================================
@login_required
def add_contact_view():
    wa_service = WhatsAppService()
    
    name = request.form.get('name', '')
    phone = request.form.get('phone', '')
    category = request.form.get('category', 'customers')
    company = request.form.get('company', '')
    city = request.form.get('city', '')
    email = request.form.get('email', '')
    notes = request.form.get('notes', '')
    
    result = wa_service.add_contact(
        name=name,
        phone=phone,
        category=category,
        city=city,
        company=company,
        email=email,
        notes=notes
    )
    
    if result.get('success'):
        flash('تمت إضافة جهة الاتصال بنجاح!', 'success')
    else:
        flash(result.get('error', 'حدث خطأ أثناء الإضافة'), 'danger')
        
    return redirect(url_for('whatsapp_service.contacts_bulk_view'))


# =========================================================================
# 3. استيراد ملف CSV
# =========================================================================
@login_required
def import_contacts_view():
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


# =========================================================================
# 4. إرسال حملة جماعية
# =========================================================================
@login_required
def send_broadcast_view():
    wa_service = WhatsAppService()
    
    campaign_name = request.form.get('campaign_name', '')
    target_category = request.form.get('target_category', 'all')
    message_text = request.form.get('message_text', '')
    
    target_phones = []
    
    if target_category == 'all' or target_category == 'customers':
        customers = WhatsAppCustomerContact.query.all()
        target_phones.extend([c.phone for c in customers])
    
    if target_category == 'all' or target_category == 'suppliers':
        suppliers = Supplier.query.all()
        target_phones.extend([s.phone for s in suppliers if s.phone])
    
    if target_category == 'all' or target_category == 'marketers':
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
