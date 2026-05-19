# coding: utf-8
# 🏢 مسارات تعميد وأرشفة الموردين السيادية - منصة محجوب أونلاين 2026

import os
import uuid
import re
from flask import Blueprint, request, jsonify, render_template, url_for, current_app
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash  # استيراد مكتبة التشفير الآمنة لحماية النظام

# 🎯 التعديل الحاسم لكسر الـ Circular Import والتوافق التام مع بوابة النماذج الموحدة:
from apps import db 
from apps.models import Supplier, Wallet  # الاستيراد المباشر والآمن بعد ضبط ملف الـ __init__.py المركزي

# تعميد البلوبرينت بالاسم المطابق تماماً لما تم استدعاؤه في الـ __init__.py للتطبيق
admin_suppliers_bp = Blueprint('add_supplier', __name__, template_folder='templates')

# الامتدادات المسموح بها لصور الوثائق والتأمين الحوكمي
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_next_sequence_codes():
    """
    دالة سيادية لحساب التسلسل القادم ديناميكياً بناءً على آخر مورد تم تعميده في النظام.
    تضمن قراءة السجلات السابقة وإكمال التسلسل الرقمي تصاعدياً دون تكرار.
    """
    try:
        # جلب آخر مورد مسجل في قاعدة البيانات للاتكاء على تسلسله
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        if last_supplier and last_supplier.sovereign_id:
            # استخراج الأرقام فقط من المعرف السيادي (مثال: SUP-MAH9631 يعيد 9631)
            match = re.search(r'\d+', last_supplier.sovereign_id)
            if match:
                next_num = int(match.group()) + 1
                return f"SUP-MAH{next_num}"
        # في حال لم يتم العثور على سجلات (كحالة احتياطية صفرية)
        return "SUP-MAH9631"
    except Exception as e:
        current_app.logger.error(f"❌ خطأ أثناء توليد التسلسل السيادي: {str(e)}")
        return "SUP-MAH9631"


@admin_suppliers_bp.route('/admin/suppliers/check-duplicate', methods=['GET'])
def check_duplicate():
    """
    نقطة الوصول اللحظية (Debounce Check) لمنع تكرار البيانات الحساسة وقراءة التسلسل التالي للواجهة.
    """
    check_type = request.args.get('type')
    value = request.args.get('value', '').strip()

    if check_type == 'get_next_sequence':
        next_sup = generate_next_sequence_codes()
        return jsonify({'next_sequence': next_sup})

    if not value:
        return jsonify({'exists': False})

    exists = False
    
    if check_type == 'username':
        exists = db.session.query(Supplier.query.filter_by(username=value).exists()).scalar()
    elif check_type == 'identity_number':
        exists = db.session.query(Supplier.query.filter_by(identity_number=value).exists()).scalar()
    elif check_type == 'owner_name':
        exists = db.session.query(Supplier.query.filter_by(owner_name=value).exists()).scalar()
    elif check_type == 'trade_name':
        exists = db.session.query(Supplier.query.filter_by(trade_name=value).exists()).scalar()
    elif check_type == 'owner_phone':
        exists = db.session.query(Supplier.query.filter_by(owner_phone=value).exists()).scalar()
    elif check_type == 'bank_acc':
        exists = db.session.query(Supplier.query.filter_by(bank_acc=value).exists()).scalar()

    return jsonify({'exists': exists})


@admin_suppliers_bp.route('/admin/suppliers/add', methods=['POST'])
def add_supplier_submit():
    """
    استقبال ومعالجة نموذج تعميد المورد وإصدار المحفظة وحفظ الوثائق سحابياً.
    """
    try:
        # 1. استخراج البيانات من الواجهة الـ HTML
        username = request.form.get('username', '').strip()
        password = request.form.get('password')  
        identity_type = request.form.get('identity_type')
        identity_number = request.form.get('identity_number', '').strip()
        
        owner_name = request.form.get('owner_name', '').strip()
        trade_name = request.form.get('trade_name', '').strip()
        owner_phone = request.form.get('owner_phone', '').strip()
        
        # تصحيح حقل هاتف المحل ليتوافق مع شرط قاعدة البيانات (nullable=False) ولا يرسل القيمة None فارغة
        shop_phone = request.form.get('shop_phone', '').strip() or owner_phone
        
        province = request.form.get('province')
        district = request.form.get('district')
        address_detail = request.form.get('address_detail', '').strip()
        
        fin_type = request.form.get('fin_type')
        bank_name = request.form.get('bank_name')
        bank_acc = request.form.get('bank_acc', '').strip()
        activity_type = request.form.get('activity_type')

        # 2. توليد المعرفات السيادية والمالية المغلقة بناءً على السجل الأخير في قاعدة البيانات
        final_sovereign_id = generate_next_sequence_codes()
        final_wallet_code = final_sovereign_id.replace("SUP-", "WEL-", 1)

        # 3. معالجة وحفظ صورة وثيقة الهوية الرقمية
        identity_image_path = None
        if 'identity_image' in request.files:
            file = request.files['identity_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"doc_{final_sovereign_id}_{uuid.uuid4().hex[:6]}_{filename}"
                
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/identities')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                    
                file.save(os.path.join(upload_folder, unique_filename))
                identity_image_path = os.path.join(upload_folder, unique_filename)

        # 4. فحص احترازي نهائي على السيرفر قبل الضخ لضمان سلامة البيانات المعمدة وعدم التكرار
        check_dup_username = Supplier.query.filter_by(username=username).first()
        if check_dup_username:
            return jsonify({'status': 'error', 'message': 'اسم المستخدم معتمد مسبقاً في النظام لحساب آخر.'}), 400

        # التعديل الحاسم لتوليد الهاش المتوافق مع حقل password_hash
        hashed_pwd = generate_password_hash(password)

        # 5. بناء السجل وضخه لقاعدة البيانات السيادية
        new_supplier = Supplier(
            sovereign_id=final_sovereign_id,
            wallet_code=final_wallet_code,
            username=username,
            password_hash=hashed_pwd,  # تم التعديل إلى الاسم الدقيق المسجل في الـ Model مع التشفير الآمن
            identity_type=identity_type,
            identity_number=identity_number,
            identity_image=identity_image_path,
            owner_name=owner_name,
            trade_name=trade_name,
            owner_phone=owner_phone,
            shop_phone=shop_phone,
            province=province,
            district=district,
            address_detail=address_detail,
            fin_type=fin_type,
            bank_name=bank_name,
            bank_acc=bank_acc,
            activity_type=activity_type,
            status='active'  # تم تعديل الحالة لتبدأ نشطة مباشرة عند التعميد من لوحة التحكم الإدارية
        )
        
        db.session.add(new_supplier)
        db.session.flush()  # حجز الكيان لاستخراج المعرف الفريد وتأمين عملية الربط المالي الفوري

        # 6. تعميد وإنشاء المحفظة الموحدة التابعة المرتبطة ماليًا بالمورد الجديد عبر الـ sovereign_id
        new_wallet = Wallet(
            supplier_id=final_sovereign_id,  # الاعتماد المباشر على كلاس Wallet الموحد والربط الحوكمي المستقر
            wallet_code=final_wallet_code,
            status='نشطة'
        )
        db.session.add(new_wallet)
        
        # إنهاء المعاملة وحفظ البيانات بشكل قطعي وثابت سحابياً
        db.session.commit()

        # 7. الاستجابة بالـ JSON المتوافق تماماً مع ميكانيكية المودال لإتمام النسخ بنجاح
        return jsonify({
            'status': 'success',
            'message': 'تم تعميد المورد بنجاح في قاعدة البيانات السيادية وصناعة المحفظة الموحدة بنجاح.',
            'data': {
                'sovereign_id': final_sovereign_id,
                'wallet_code': final_wallet_code
            },
            'redirect_url': url_for('add_supplier.admin_suppliers_list')
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Sovereign Archive Error: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'فشل في حفظ البيانات السحابية: {str(e)}'
        }), 500


@admin_suppliers_bp.route('/admin/suppliers/list')
def admin_suppliers_list():
    """
    عرض وأرشفة الموردين المعتمدين في النظام - المسار المتوافق مع المتصفح لحل الـ 404 والـ 500.
    """
    return render_template('admin_suppliers_list.html')
