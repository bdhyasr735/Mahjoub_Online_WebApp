# apps/add_supplier/routes.py
# coding: utf-8

from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash

# استيراد قاعدة البيانات والموديل
from apps import db  
from apps.models.supplier_db import Supplier 

# استيراد البلوبرينت الموحد والمثبت من ملف الـ __init__ لمنع التعارض الخفي
from apps.add_supplier import admin_suppliers

@admin_suppliers.route('/add', methods=['GET', 'POST'])
@login_required 
def add_supplier():
    """
    محرك تعميد الموردين: يقوم بمعالجة البيانات وحفظها في السجل لـ "منصة محجوب أونلاين"
    """
    if request.method == 'POST':
        try:
            # 1. استقبال البيانات الأساسية وتطهيرها من الفراغات
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

            # 4. تشفير كلمة المرور وتجهيز الكائن
            hashed_pw = generate_password_hash(password)
            
            new_supplier = Supplier(
                sovereign_id="PENDING", 
                username=username,
                password_hash=hashed_pw,
                identity_type=identity_type,
                identity_number=identity_number,
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
                status='المراجعة',        # إجبار إسناد حالة البدء الافتراضية لحوكمة النظام
                rank_grade='ريادي',       # إجبار إسناد رتبة المورد الأولى للتحكم بالصلاحيات
                registration_source='لوحة التحكم', # تحديد ولادة الحساب من الإدارة
                created_by_id=getattr(current_user, 'id', None), 
                created_at=datetime.utcnow()
            )

            # 5. معالجة المرفقات
            if 'identity_image' in request.files:
                file = request.files['identity_image']
                if file and file.filename != '':
                    pass

            # 6. الحفظ النهائي المؤكد في قاعدة البيانات
            db.session.add(new_supplier)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': 'تم تعميد المورد بنجاح في نظام الأرشفة',
                'data': {
                    'username': new_supplier.username,
                    'sovereign_id': new_supplier.sovereign_id
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            print(f"Critical Error in add_supplier: {str(e)}")
            return jsonify({'status': 'error', 'message': f'فشل في عملية التعميد: {str(e)}'}), 500

    # -------------------------------------------------------------------------
    # في حالة GET: حساب التنبؤ الرقمي السيادي بناءً على آخر سجل حقيقي في القاعدة
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
        print(f"Error fetching next_sovereign_id prediction: {str(e)}")
        next_sovereign_id = "SUP-WEL-MAH96319"
    
    return render_template('admin/add_supplier.html', sovereign_id=next_sovereign_id)


@admin_suppliers.route('/check-duplicate', methods=['GET'])
@login_required
def check_duplicate():
    """
    نظام الفحص اللحظي الآمن والمطور: يتصل به الـ JavaScript عند الكتابة لإظهار (✅/❌)
    ويشمل حوكمة طول النص ومنع تكرار البيانات مع تصفية الفراغات تماماً.
    """
    try:
        check_type = request.args.get('type')
        value = request.args.get('value', '').strip()

        if not check_type or not value:
            return jsonify({'exists': False, 'valid': False, 'message': 'الحقل فارغ'})

        # حوكمة إضافية في الـ Back-end لاسم المستخدم: إذا قل عن 3 أحرف يسقط كـ "غير صالح وموجود" فوراً
        if check_type == 'username' and len(value) < 3:
            return jsonify({'exists': True, 'valid': False, 'message': 'اسم المستخدم قصير جداً'})

        # خريطة الحقول الشاملة: تم دعم كلا حقول الهاتف (owner_phone و shop_phone) لضمان دقة الاستجابة
        field_map = {
            'username': Supplier.username,
            'trade_name': Supplier.trade_name,
            'shop_phone': Supplier.shop_phone,
            'owner_phone': Supplier.owner_phone,
            'identity_number': Supplier.identity_number,
            'bank_acc': Supplier.bank_acc
        }

        target_field = field_map.get(check_type)
        exists = False
        
        if target_field is not None:
            exists = Supplier.query.filter(target_field == value).first() is not None

        return jsonify({'exists': exists, 'valid': not exists})
        
    except Exception as e:
        print(f"Check duplicate error for {check_type}: {str(e)}")
        return jsonify({'exists': False, 'error': str(e), 'valid': False})
