import os
from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime
from werkzeug.utils import secure_filename

# استيراد قاعدة البيانات والموديل من المسار الذي حددته
from models.supplier_db import db, Supplier 

admin_suppliers = Blueprint('admin_suppliers', __name__)

@admin_suppliers.route('/admin/suppliers/add', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        try:
            # 1. استلام البيانات من نموذج التعميد
            unified_id = request.form.get('unified_id')
            username = request.form.get('username')
            password = request.form.get('password')
            
            # معالجة فئة المورد (يدوي أو اختيار من القائمة)
            category = request.form.get('category')
            if category == 'manual':
                category = request.form.get('manual_category')

            # 2. بيانات المالك والمنشأة والاتصال
            owner_name = request.form.get('owner_name')
            trade_name = request.form.get('trade_name')
            shop_phone = request.form.get('shop_phone')
            
            # 3. بيانات الموقع الجغرافي
            province = request.form.get('province')
            district = request.form.get('district')
            address_detail = request.form.get('address_detail')

            # 4. بيانات الربط المالي (بنوك / صرافة)
            fin_type = request.form.get('fin_type')
            bank_name = request.form.get('bank_name')
            bank_acc = request.form.get('bank_acc')

            # 5. معالجة صورة الوثيقة (إن وجدت)
            identity_image = request.files.get('identity_image')
            image_filename = None
            if identity_image and identity_image.filename != '':
                image_filename = secure_filename(f"{unified_id}_{identity_image.filename}")
                # ملاحظة: يجب إعداد UPLOAD_FOLDER في ملف التكوين الرئيسي (app.config)
                # identity_image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))

            # 6. إنشاء كائن المورد الجديد وحفظه في المحرك
            new_supplier = Supplier(
                sovereign_id=unified_id,
                username=username,
                password=password, # يفضل استخدام التشفير Werkzeug security
                category=category,
                owner_name=owner_name,
                trade_name=trade_name,
                shop_phone=shop_phone,
                province=province,
                district=district,
                address_detail=address_detail,
                finance_type=fin_type,
                bank_name=bank_name,
                bank_account=bank_acc,
                identity_image=image_filename,
                created_at=datetime.utcnow()
            )

            db.session.add(new_supplier)
            db.session.commit()

            # 7. استجابة النجاح المتوافقة مع Modal الجافاسكريبت في القالب
            return jsonify({
                'status': 'success',
                'data': {
                    'sovereign_id': unified_id,
                    'username': username,
                    'password': password
                }
            })

        except Exception as e:
            # تراجع عن العملية في حالة حدوث أي خلل تقني
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'فشل في عملية التعميد: {str(e)}'
            }), 400

    # في حالة GET: عرض الصفحة مع حساب المعرف التسلسلي القادم
    try:
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        next_id_num = (last_supplier.id + 1) if last_supplier else 1
    except:
        next_id_num = 1
        
    return render_template('admin/add_supplier.html', next_id=next_id_num)

@admin_suppliers.route('/admin/suppliers/check-duplicate/', methods=['GET'])
def check_duplicate():
    """محرك فحص التكرار اللحظي لضمان جودة البيانات السيادية"""
    field_type = request.args.get('type')
    value = request.args.get('value')
    
    if not value:
        return jsonify({'exists': False})

    query_filter = {field_type: value}
    exists = Supplier.query.filter_by(**query_filter).first() is not None
    return jsonify({'exists': exists})
