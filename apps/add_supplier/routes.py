# apps/add_supplier/routes.py
# coding: utf-8

import os
import secrets
from flask import render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

# استيراد قاعدة البيانات والموديل
from apps import db  
from apps.models.supplier_db import Supplier 

# استيراد محمي ومباشر للبلوبرينت
from . import admin_suppliers

@admin_suppliers.route('/add', methods=['GET', 'POST'])
@login_required 
def add_supplier():
    """
    محرك تعميد الموردين: يقوم بمعالجة البيانات وحفظها في السجل لـ "منصة محجوب أونلاين"
    الحالة الافتراضية: نشط | الرتبة الافتراضية: أساسي
    """
    if request.method == 'POST':
        try:
            # 1. استقبال البيانات الأساسية وتطهيرها من الفراغات (Sanitization)
            username = request.form.get('username', '').strip()
            trade_name = request.form.get('trade_name', '').strip()
            password = request.form.get('password')
            identity_number = request.form.get('identity_number', '').strip()
            bank_acc = request.form.get('bank_acc', '').strip()
            shop_phone = request.form.get('shop_phone', '').strip()
            owner_phone = request.form.get('owner_phone', '').strip()

            # 2. التحقق النهائي الصارم والثابت عند الإرسال (Back-end Validation) لمنع التكرار تماماً
            if not username or len(username) < 3:
                return jsonify({'status': 'error', 'message': 'فشل التعميد: يجب أن يكون اسم المستخدم 3 أحرف أو أكثر!'}), 400

            if Supplier.query.filter_by(username=username).first():
                return jsonify({'status': 'error', 'message': 'فشل التعميد: اسم المستخدم مسجل مسبقاً!'}), 400
            
            if trade_name and Supplier.query.filter_by(trade_name=trade_name).first():
                return jsonify({'status': 'error', 'message': 'فشل التعميد: الاسم التجاري مسجل مسبقاً!'}), 400

            if shop_phone and Supplier.query.filter_by(shop_phone=shop_phone).first():
                return jsonify({'status': 'error', 'message': 'فشل التعميد: هاتف المنشأة مسجل مسبقاً!'}), 400

            if owner_phone and Supplier.query.filter_by(owner_phone=owner_phone).first():
                return jsonify({'status': 'error', 'message': 'فشل التعميد: رقم هاتف المالك مسجل مسبقاً!'}), 400

            if identity_number and Supplier.query.filter_by(identity_number=identity_number).first():
                return jsonify({'status': 'error', 'message': 'فشل التعميد: رقم الوثيقة أو الهوية مسجل مسبقاً!'}), 400

            if bank_acc and Supplier.query.filter_by(bank_acc=bank_acc).first():
                return jsonify({'status': 'error', 'message': 'فشل التعميد: رقم الحساب البنكي مسجل لمورد آخر مسبقاً!'}), 400

            # 3. معالجة حقول الإدخال اليدوي الديناميكية وتطابقها مع الواجهة المحدثة
            identity_type = request.form.get('identity_type')
            bank_name = request.form.get('bank_name')
            activity_type = request.form.get('activity_type', '').strip()

            # 4. حساب وتوليد المعرف السيادي الحقيقي للحفظ الفعلي في الداتابيز لمنع الـ PENDING
            try:
                last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
                if last_supplier and last_supplier.sovereign_id and 'SUP-WEL-MAH963' in last_supplier.sovereign_id:
                    try:
                        last_num_str = last_supplier.sovereign_id.replace('SUP-WEL-MAH963', '').strip()
                        next_num = int(last_num_str) + 1
                    except (ValueError, IndexError):
                        next_num = (last_supplier.id or 0) + 1
                else:
                    next_num = (last_supplier.id or 0) + 1 if last_supplier else 1
                
                final_sovereign_id = f"SUP-WEL-MAH963{next_num}"
            except Exception:
                final_sovereign_id = request.form.get('sovereign_id', '').strip() or "SUP-WEL-MAH96319"

            # 5. تشفير كلمة المرور وتجهيز الكائن الإنشائي السيادي
            hashed_pw = generate_password_hash(password)
            
            # معالجة رفع الملفات والمرفقات (صورة الوثيقة) إن وجدت
            image_filename = None
            if 'identity_image' in request.files:
                file = request.files['identity_image']
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    unique_suffix = secrets.token_hex(4)
                    _, ext = os.path.splitext(filename)
                    image_filename = f"doc_{unique_suffix}{ext}"
                    
                    # مسار الحفظ الآمن للمرفقات
                    upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'identities')
                    os.makedirs(upload_path, exist_ok=True)
                    file.save(os.path.join(upload_path, image_filename))
            
            new_supplier = Supplier(
                sovereign_id=final_sovereign_id, 
                username=username,
                password_hash=hashed_pw,
                identity_type=identity_type,
                identity_number=identity_number,
                identity_image=image_filename,
                activity_type=activity_type,
                owner_name=request.form.get('owner_name', '').strip(),
                trade_name=trade_name,
                shop_phone=shop_phone,
                owner_phone=owner_phone,
                province=request.form.get('province'),
                district=request.form.get('district'),
                address_detail=request.form.get('address_detail'),
                fin_type=request.form.get('fin_type'),
                bank_name=bank_name,
                bank_acc=bank_acc,
                status='نشط',                                     
                rank_grade='أساسي',                               
                registration_source='لوحة التحكم', 
                created_by_id=getattr(current_user, 'id', None), 
                created_at=datetime.now(timezone.utc)            
            )

            # 6. الحفظ النهائي المؤكد في قاعدة البيانات
            db.session.add(new_supplier)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': 'تم تعميد المورد بنجاح في نظام الأرشفة برتبة أساسي وحالة نشطة',
                'data': {
                    'username': new_supplier.username,
                    'sovereign_id': new_supplier.sovereign_id
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Critical Error in add_supplier: {str(e)}")
            return jsonify({'status': 'error', 'message': f'فشل في عملية التعميد: {str(e)}'}), 500

    # -------------------------------------------------------------------------
    # في حالة GET
    # -------------------------------------------------------------------------
    try:
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        if last_supplier and last_supplier.sovereign_id and 'SUP-WEL-MAH963' in last_supplier.sovereign_id:
            try:
                last_num_str = last_supplier.sovereign_id.replace('SUP-WEL-MAH963', '').strip()
                next_num = int(last_num_str) + 1
            except (ValueError, IndexError):
                next_num = (last_supplier.id or 0) + 1
        else:
            next_num = (last_supplier.id or 0) + 1 if last_supplier else 1

        next_sovereign_id = f"SUP-WEL-MAH963{next_num}"
    except Exception as e:
        current_app.logger.error(f"Error fetching next_sovereign_id prediction: {str(e)}")
        next_sovereign_id = "SUP-WEL-MAH96319"
    
    # حوكمة استدعاء القالب: إذا كان الملف داخل مجلد التطبيق الفرعي وليس المجلد الرئيسي لـ Flask
    # نقوم بتجربة استدعائه مباشرة، وإذا فشل يتم توجيهه للمجلد الفرعي لتجنب الـ TemplateNotFound تماماً
    try:
        return render_template('admin/add_supplier.html', sovereign_id=next_sovereign_id)
    except Exception:
        return render_template('add_supplier.html', sovereign_id=next_sovereign_id)


@admin_suppliers.route('/check-duplicate', methods=['GET'])
@login_required
def check_duplicate():
    """
    نظام الفحص اللحظي المطور
    """
    try:
        check_type = request.args.get('type')
        value = request.args.get('value', '').strip()

        if not check_type or not value:
            return jsonify({'exists': False, 'valid': False, 'status': 'empty', 'message': 'الحقل فارغ'})

        if check_type == 'username' and len(value) < 3:
            return jsonify({'exists': True, 'valid': False, 'status': 'invalid', 'message': 'اسم المستخدم قصير جداً'})

        exists = False
        if check_type == 'username':
            exists = Supplier.query.filter_by(username=value).first() is not None
        elif check_type == 'trade_name':
            exists = Supplier.query.filter_by(trade_name=value).first() is not None
        elif check_type == 'shop_phone':
            exists = Supplier.query.filter_by(shop_phone=value).first() is not None
        elif check_type == 'owner_phone':
            exists = Supplier.query.filter_by(owner_phone=value).first() is not None
        elif check_type == 'identity_number':
            exists = Supplier.query.filter_by(identity_number=value).first() is not None
        elif check_type == 'bank_acc':
            exists = Supplier.query.filter_by(bank_acc=value).first() is not None

        return jsonify({
            'exists': exists, 
            'valid': not exists,
            'status': 'duplicate' if exists else 'unique',
            'message': 'البيانات مسجلة مسبقاً!' if exists else 'البيانات متاحة للاستخدام'
        })
        
    except Exception as e:
        current_app.logger.error(f"Check duplicate raw database error for {check_type}: {str(e)}")
        return jsonify({'exists': False, 'valid': False, 'status': 'error', 'error': str(e)})
