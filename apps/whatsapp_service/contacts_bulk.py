# coding: utf-8
# 📂 apps/whatsapp_service/contacts_bulk.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from apps.extensions import db
from apps.models.whatsapp_models import WhatsAppCustomerContact
from apps.models.supplier_db import Supplier
from apps.models.marketer_db import Marketer
from flask_login import login_required, current_user

contacts_bp = Blueprint('whatsapp_service', __name__, template_folder='../templates')

# ==========================================
# 1. صفحة عرض جهات الاتصال
# ==========================================
@contacts_bp.route('/admin/whatsapp/contacts-bulk', methods=['GET'])
@login_required
def contacts_bulk():
    # قراءة الفلتر من الرابط
    current_category = request.args.get('category', 'all')
    
    # جلب بيانات العملاء (WhatsAppCustomerContact)
    customers_query = WhatsAppCustomerContact.query
    if current_category != 'all':
        customers_query = customers_query.filter_by(category=current_category) # تأكد من وجود هذا الحقل في Model الخاص بك
    customers = customers_query.order_by(WhatsAppCustomerContact.created_at.desc()).all()

    # جلب بيانات الموردين (Supplier)
    suppliers = Supplier.query.order_by(Supplier.created_at.desc()).all()
    
    # جلب بيانات المسوقين (Marketer)
    marketers = Marketer.query.order_by(Marketer.created_at.desc()).all()
    
    # دمج جميع جهات الاتصال في قائمة واحدة للعرض (إذا كانت الصفحة تعرضها معاً)
    # ملاحظة: إذا كانت قاعدة بياناتك تستخدم فئات مختلفة، يجب تحويلها إلى توحيد القائمة هنا
    # للتبسيط، سنفترض أنك تعرضها كمجموعات في القالب، لذا سنمررها منفصلة
    all_contacts = [] 
    
    # حساب الإحصائيات
    stats = {
        'customers_count': customers_query.count() if current_category == 'all' else len(customers),
        'merchants_count': Supplier.query.count(),
        'suppliers_count': Supplier.query.count(), # نفس جدول الموردين حسب الـ Model
        'marketers_count': Marketer.query.count(),
    }

    return render_template('admin/contacts_bulk.html',
                           contacts=all_contacts,  # لاستخدامها في الجدول أو القالب
                           customers=customers,
                           suppliers=suppliers,
                           marketers=marketers,
                           stats=stats,
                           current_category=current_category)


# ==========================================
# 2. إضافة جهة اتصال جديدة
# ==========================================
@contacts_bp.route('/admin/whatsapp/add_contact', methods=['POST'])
@login_required
def add_contact():
    # استقبال البيانات من النموذج
    name = request.form.get('name')
    phone = request.form.get('phone')
    category = request.form.get('category', 'customers')
    company = request.form.get('company')
    city = request.form.get('city')
    status = request.form.get('status', 'active')
    discount_code = request.form.get('discount_code')
    tags = request.form.get('tags')
    notes = request.form.get('notes')
    
    try:
        # إذا كانت الفئة عميل: احفظ في WhatsAppCustomerContact
        if category == 'customers':
            new_contact = WhatsAppCustomerContact(
                name=name,
                phone=phone,
                last_message=None,
                is_blocked=False if status == 'active' else True,
                notes=notes,
                tags=[t.strip() for t in tags.split(',')] if tags else [],
                extra_data={'company': company, 'city': city, 'discount_code': discount_code}
            )
            db.session.add(new_contact)
            
        # إذا كانت الفئة تاجر/مورد: احفظ في Supplier
        elif category in ['merchants', 'suppliers']:
            new_supplier = Supplier(
                username=phone,
                store_name=name,
                owner_name=name,
                search_phone=phone[-9:],
                phone=phone,  # يتم تشفيره تلقائياً في الـ setter
                status=status,
                rank='bronze'
            )
            new_supplier.set_password('default123')  # كلمة مرور افتراضية مؤقتة
            db.session.add(new_supplier)
            
        # إذا كانت الفئة مسوق: احفظ في Marketer
        elif category == 'marketers':
            new_marketer = Marketer(
                full_name=name,
                marketing_code=f"MKT-{int(datetime.utcnow().timestamp())}",
                phone=phone,
                is_active=True if status == 'active' else False
            )
            new_marketer.set_password('default123')
            db.session.add(new_marketer)
            
        db.session.commit()
        flash('تمت إضافة جهة الاتصال بنجاح!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء الإضافة: {str(e)}', 'danger')
        
    return redirect(url_for('whatsapp_service.contacts_bulk'))


# ==========================================
# 3. استيراد جهات الاتصال (CSV)
# ==========================================
@contacts_bp.route('/admin/whatsapp/import_contacts', methods=['POST'])
@login_required
def import_contacts():
    file = request.files.get('file')
    default_category = request.form.get('default_category', 'customers')
    
    if not file:
        flash('يرجى رفع ملف أولاً', 'danger')
        return redirect(url_for('whatsapp_service.contacts_bulk'))
    
    # هنا كود قراءة الملف وإدخال البيانات (يمكن استخدام pandas أو csv)
    # مثال بسيط:
    import csv
    import io
    
    try:
        stream = io.StringIO(file.read().decode("UTF-8"))
        reader = csv.DictReader(stream)
        
        for row in reader:
            name = row.get('Name') or row.get('name')
            phone = row.get('Phone') or row.get('phone')
            category = row.get('Category', default_category)
            
            if name and phone:
                if category == 'customers':
                    contact = WhatsAppCustomerContact(name=name, phone=phone)
                    db.session.add(contact)
                else:
                    supplier = Supplier(username=phone, store_name=name, phone=phone, status='active')
                    supplier.set_password('default123')
                    db.session.add(supplier)
                    
        db.session.commit()
        flash('تم استيراد جهات الاتصال بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في الاستيراد: {str(e)}', 'danger')
        
    return redirect(url_for('whatsapp_service.contacts_bulk'))


# ==========================================
# 4. حذف جهة اتصال (عبر POST)
# ==========================================
@contacts_bp.route('/admin/whatsapp/delete_contact/<int:id>', methods=['POST'])
@login_required
def delete_contact(id):
    # تحديد الجدول حسب الفئة أو البحث في جميع الجداول
    contact = WhatsAppCustomerContact.query.get(id)
    if not contact:
        contact = Supplier.query.get(id)
    if not contact:
        contact = Marketer.query.get(id)
        
    if contact:
        db.session.delete(contact)
        db.session.commit()
        flash('تم حذف جهة الاتصال', 'success')
    else:
        flash('لم يتم العثور على جهة الاتصال', 'danger')
        
    return redirect(url_for('whatsapp_service.contacts_bulk'))
