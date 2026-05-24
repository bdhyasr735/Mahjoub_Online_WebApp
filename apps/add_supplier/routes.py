# coding: utf-8
import re  # استيراد مكتبة العبارات المنتظمة لاستخراج الرقم الموحد 🎯
from flask import render_template, request, jsonify, current_app, url_for, redirect
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash  # قفل أمني لتشفير كلمات المرور 🔒
import os

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
from . import admin_suppliers_bp 

# =======================================================
# 1. دالة العرض المصلحة (تأمين ظهور واستقرار القالب)
# =======================================================
@admin_suppliers_bp.route('/add_supplier_page', methods=['GET'])
@login_required
def add_supplier_page():
    """
    مِحرّك جلب وعرض قالب تعميد الموردين.
    تمت إضافة سياق المالك والتأمين الكامل لمنع انهيار Jinja2 عند الوراثة.
    """
    # تأمين سياق المالك (المؤسس علي) المتوقع في قالب admin_base.html الأساسي
    owner_context = {
        "full_name": getattr(current_user, 'full_name', 'المؤسس علي محجوب')
    }
    
    # استدعاء القالب مع تمرير السياق الحاكم
    return render_template('admin/add_supplier.html', owner=owner_context)


# =======================================================
# 2. دالة التحقق من التكرار والـ Sequences (تطابق الجزء الرقمي التوأم)
# =======================================================
@admin_suppliers_bp.route('/check_duplicate', methods=['GET'])
@login_required
def check_duplicate():
    check_type = request.args.get('type')
    value = request.args.get('value')
    
    # جلب التسلسلات التالية المتوقعة متطابقة رقمياً
    if check_type == 'get_next_sequence':
        # 1. توليد كود المورد المعتمد من الموديل (مثل: SUP-MAH9635)
        next_sovereign = Supplier.generate_next_sovereign_id()
        
        # 2. استخراج الأرقام فقط من كود المورد لتوحيدها مع المحفظة
        supplier_digits = re.findall(r'\d+', str(next_sovereign))
        if supplier_digits:
            clean_num = supplier_digits[0]
        else:
            # احتياطي في حال فشل الاستخراج
            clean_num = "9635"
            
        return jsonify({
            'next_sequence': next_sovereign,
            'next_wallet': f"WLT-MAH{clean_num}"  # إنتاج كود المحفظة التوأم رقمياً بالبادئة الصحيحة
        })

    # التحقق الحوكمة الصارم من وجود البيانات مسبقاً لمنع التكرار (الـ 7 حقول المعتمدة)
    exists = False
    if value and value.strip() != '':
        value_striped = value.strip()
        if check_type == 'username':
            exists = Supplier.query.filter_by(username=value_striped).first() is not None
        elif check_type == 'owner_name':
            exists = Supplier.query.filter_by(owner_name=value_striped).first() is not None
        elif check_type == 'owner_phone':
            exists = Supplier.query.filter_by(owner_phone=value_striped).first() is not None
        elif check_type == 'trade_name':
            exists = Supplier.query.filter_by(trade_name=value_striped).first() is not None
        elif check_type == 'shop_number':
            exists = Supplier.query.filter_by(shop_number=value_striped).first() is not None
        elif check_type == 'identity_number':
            exists = Supplier.query.filter_by(identity_number=value_striped).first() is not None
        elif check_type == 'bank_acc':
            exists = Supplier.query.filter_by(bank_acc=value_striped).first() is not None
        
    # الباك إند يرد بـ available متوافقاً مع جافاسكريبت الواجهة الأمامية
    return jsonify({'available': not bool(exists)})


# =======================================================
# 3. دالة التنفيذ (التعميد المزدوج للمورد ومحفظته الإستراتيجية)
# =======================================================
@admin_suppliers_bp.route('/add_supplier_submit', methods=['POST'])
@login_required
def add_supplier_submit():
    try:
        # البيانات الأساسية من النموذج
        sovereign_id = request.form.get('sovereign_id')
        wallet_code = request.form.get('wallet_code')
        
        # معالجة وحفظ وثائق الهوية المرفوعة (دعم الملفات المتعددة الأوجه والظهر)
        uploaded_files = request.files.getlist('identity_images')
        saved_filenames = []
        
        upload_path = current_app.config.get('UPLOAD_FOLDER', 'apps/static/uploads')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
            
        for file in uploaded_files:
            if file and file.filename != '':
                filename = secure_filename(f"{sovereign_id}_{file.filename}")
                file.save(os.path.join(upload_path, filename))
                saved_filenames.append(filename)
        
        # دمج أسماء الملفات بفاصلة لتخزينها في حقل نصي واحد بقاعدة البيانات
        identity_image_str = ",".join(saved_filenames) if saved_filenames else None

        # تشفير كلمة المرور بشكل آمن تماماً قبل كتابتها في داتابيز السيستم
        raw_password = request.form.get('password')
        hashed_password = generate_password_hash(raw_password) if raw_password else ""

        # إنشاء كائن المورد بالمسميات الحقيقية للموديل المستقر ✅
        new_supplier = Supplier(
            sovereign_id=sovereign_id,
            username=request.form.get('username'),
            password_hash=hashed_password,  # الحقل الآمن المعتمد
            identity_type=request.form.get('identity_type'),
            identity_number=request.form.get('identity_number'),
            identity_image=identity_image_str,  # تخزين روابط الصور المرفوعة
            owner_name=request.form.get('owner_name'),
            owner_phone=request.form.get('owner_phone'),
            trade_name=request.form.get('trade_name'),
            shop_number=request.form.get('shop_number'),  # ربط مباشر مع رقم المحل المفحوص والجديد
            shop_phone=request.form.get('owner_phone'),  # الاعتماد المباشر لهاتف المالك كحقل إلزامي
            province=request.form.get('province'),
            district=request.form.get('district'),
            address_detail=request.form.get('detailed_address'),  # متوافق مع الحقل الجديد بالواجهة
            bank_name=request.form.get('bank_name'),
            bank_acc=request.form.get('bank_acc'),
            wallet_code=wallet_code
        )

        db.session.add(new_supplier)
        
        # إنشاء المحفظة المالية المرتبطة لشركاء النجاح
        new_wallet = SupplierWallet(
            supplier_id=sovereign_id,
            wallet_code=wallet_code,
            status='نشطة',
            balance=0.0
        )
        db.session.add(new_wallet)
        
        # التزام وحفظ الذرة المترابطة في قاعدة البيانات (Atomic Commit)
        db.session.commit()
        
        # جلب التسلسلات القادمة تلقائياً لإرسالها للواجهة لتحديث العدادات الفورية بعد نجاح الحفظ
        next_sovereign = Supplier.generate_next_sovereign_id()
        supplier_digits = re.findall(r'\d+', str(next_sovereign))
        clean_num = supplier_digits[0] if supplier_digits else "9636"
        next_wallet_code = f"WLT-MAH{clean_num}"
        
        return jsonify({
            'status': 'success', 
            'message': f'تم تعميد شريك النجاح بنجاح - المعرف السيادي: {sovereign_id}',
            'next_sequence': next_sovereign,
            'next_wallet': next_wallet_code
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في تعميد المورد: {str(e)}")
        return jsonify({'status': 'error', 'message': f'حدث خطأ تقني أثناء معالجة الطلب: {str(e)}'})
