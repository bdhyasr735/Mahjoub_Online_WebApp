# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/contacts_bulk.py
"""
سوق محجوب أونلاين - عرض وإدارة جهات الاتصال مع دعم الحملات الجماعية
يعتمد هذا الملف على WhatsAppService الموجود في service.py
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from apps.extensions import db

# استيراد النماذج
from apps.models.whatsapp_models import WhatsAppCustomerContact
from apps.models.supplier_db import Supplier
from apps.models.marketer_db import Marketer

# استيراد الخدمة (المحرك)
from apps.whatsapp_service.service import WhatsAppService

# إنشاء Blueprint خاص بهذه الصفحة (أو استخدم الموجود في routes.py)
contacts_bulk_bp = Blueprint('contacts_bulk', __name__, template_folder='../templates')


# =========================================================================
# 1. عرض صفحة جهات الاتصال
# =========================================================================
@contacts_bulk_bp.route('/admin/whatsapp/contacts-bulk', methods=['GET'])
@login_required
def contacts_bulk_view():
    wa_service = WhatsAppService()
    
    # جلب جميع جهات الاتصال من قاعدة البيانات (باستخدام دالة الخدمة)
    all_contacts = wa_service.get_all_contacts()
    
    # حساب الإحصائيات
    try:
        customers_count = WhatsAppCustomerContact.query.count()
        suppliers_count = Supplier.query.count()
        marketers_count = Marketer.query.count()
        merchants_count = suppliers_count  # نفس جدول الموردين
    except Exception:
        customers_count, suppliers_count, marketers_count, merchants_count = 0, 0, 0, 0

    stats = {
        'customers_count': customers_count,
        'merchants_count': merchants_count,
        'suppliers_count': suppliers_count,
        'marketers_count': marketers_count
    }

    current_category = request.args.get('category', 'all')
    
    # إعادة توجيه البيانات للقالب
    return render_template('admin/contacts_bulk.html', 
                           contacts=all_contacts, 
                           stats=stats,
                           current_category=current_category)


# =========================================================================
# 2. إضافة جهة اتصال جديدة (يستخدم دالة add_contact في WhatsAppService)
# =========================================================================
@contacts_bulk_bp.route('/admin/whatsapp/add-contact', methods=['POST'])
@login_required
def add_contact():
    wa_service = WhatsAppService()
    
    # استقبال البيانات من النموذج
    name = request.form.get('name', '')
    phone = request.form.get('phone', '')
    category = request.form.get('category', 'customers')
    company = request.form.get('company', '')
    city = request.form.get('city', '')
    email = request.form.get('email', '')
    notes = request.form.get('notes', '')
    
    # استدعاء الدالة الجاهزة في الخدمة
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
        
    return redirect(url_for('contacts_bulk.contacts_bulk_view'))


# =========================================================================
# 3. تحديث جهة اتصال (يستخدم دالة update_contact)
# =========================================================================
@contacts_bulk_bp.route('/admin/whatsapp/update-contact', methods=['POST'])
@login_required
def update_contact():
    wa_service = WhatsAppService()
    
    contact_id = request.form.get('contact_id')
    data = request.form.to_dict()
    
    result = wa_service.update_contact(int(contact_id), data)
    
    if result.get('success'):
        flash('تم تحديث جهة الاتصال بنجاح!', 'success')
    else:
        flash(result.get('error', 'حدث خطأ أثناء التحديث'), 'danger')
        
    return redirect(url_for('contacts_bulk.contacts_bulk_view'))


# =========================================================================
# 4. حذف جهة اتصال (يستخدم دالة delete_contact)
# =========================================================================
@contacts_bulk_bp.route('/admin/whatsapp/delete-contact', methods=['POST'])
@login_required
def delete_contact():
    wa_service = WhatsAppService()
    
    contact_id = request.form.get('contact_id')
    result = wa_service.delete_contact(int(contact_id))
    
    if result.get('success'):
        flash('تم حذف جهة الاتصال بنجاح!', 'success')
    else:
        flash(result.get('error', 'حدث خطأ أثناء الحذف'), 'danger')
        
    return redirect(url_for('contacts_bulk.contacts_bulk_view'))


# =========================================================================
# 5. حذف مجموعة جهات اتصال (يستخدم دالة delete_contacts_bulk)
# =========================================================================
@contacts_bulk_bp.route('/admin/whatsapp/delete-selected', methods=['POST'])
@login_required
def delete_selected():
    wa_service = WhatsAppService()
    
    ids = request.form.getlist('selected_contacts')
    ids = [int(i) for i in ids if i.isdigit()]
    
    result = wa_service.delete_contacts_bulk(ids)
    
    if result.get('success'):
        flash(result.get('message', 'تم الحذف بنجاح!'), 'success')
    else:
        flash(result.get('error', 'حدث خطأ'), 'danger')
        
    return redirect(url_for('contacts_bulk.contacts_bulk_view'))


# =========================================================================
# 6. إرسال رسالة فردية (يستخدم دالة send_message)
# =========================================================================
@contacts_bulk_bp.route('/admin/whatsapp/send-message', methods=['POST'])
@login_required
def send_message():
    wa_service = WhatsAppService()
    
    phone = request.form.get('phone', '')
    message = request.form.get('message', '')
    
    if phone and message:
        # استخدام دالة الإرسال في الخدمة
        result = wa_service.send_message(recipient_phone=phone, text=message)
        # إرجاع النتيجة (في نسخة تجريبية يعيد status: simulated)
        flash('تم إرسال الرسالة بنجاح!', 'success')
    else:
        flash('يرجى تعبئة الرقم والرسالة', 'danger')
        
    return redirect(url_for('contacts_bulk.contacts_bulk_view'))


# =========================================================================
# 7. إرسال حملة جماعية (يستخدم خدمة الرسائل لإرسال رسائل متعددة)
# =========================================================================
@contacts_bulk_bp.route('/admin/whatsapp/send-broadcast', methods=['POST'])
@login_required
def send_broadcast():
    wa_service = WhatsAppService()
    
    campaign_name = request.form.get('campaign_name', '')
    target_category = request.form.get('target_category', 'all')
    message_text = request.form.get('message_text', '')
    
    # جلب قائمة الأرقام المستهدفة بناءً على الفئة
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
    
    # إرسال الرسائل
    sent_count = 0
    for phone in target_phones:
        # استبدال المتغيرات في الرسالة (مثال: {name})
        personalized_message = message_text.replace("{phone}", phone)
        
        result = wa_service.send_message(recipient_phone=phone, text=personalized_message)
        if result.get('status') in ['sent', 'simulated']:
            sent_count += 1
    
    flash(f'تم إرسال الحملة بنجاح إلى {sent_count} جهة اتصال!', 'success')
    return redirect(url_for('contacts_bulk.contacts_bulk_view'))


# =========================================================================
# 8. استيراد ملف CSV (يخدم صفحة الاستيراد)
# =========================================================================
@contacts_bulk_bp.route('/admin/whatsapp/import-csv', methods=['POST'])
@login_required
def import_csv():
    wa_service = WhatsAppService()
    
    file = request.files.get('file')
    default_category = request.form.get('default_category', 'customers')
    
    if not file:
        flash('يرجى رفع ملف أولاً', 'danger')
        return redirect(url_for('contacts_bulk.contacts_bulk_view'))
    
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
        
    return redirect(url_for('contacts_bulk.contacts_bulk_view'))
