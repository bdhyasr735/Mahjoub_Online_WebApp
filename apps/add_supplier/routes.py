import os
from flask import render_template, request, jsonify, url_for, current_app
from apps import db  # تأكد من استيراد كائن قاعدة البيانات الخاص بك
from apps.models import User, Supplier  # استيراد الموديلات
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

# إذا كنت تستخدم Blueprint، تأكد من تعريفه هنا
# from apps.add_supplier import blueprint

def add_supplier_route():
    """
    المنطق البرمجي لإضافة مورد جديد في نظام محجوب أونلاين (Flask Version)
    """
    if request.method == 'POST':
        try:
            # 1. استلام البيانات النصية من النموذج
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
            activity_type = request.form.get('activity_type')
            owner_name = request.form.get('owner_name')
            identity_type = request.form.get('identity_type')
            trade_name = request.form.get('trade_name')
            phone = request.form.get('phone')
            bank_name = request.form.get('bank_name')
            bank_acc = request.form.get('bank_acc')
            province = request.form.get('province')
            district = request.form.get('district')
            address_detail = request.form.get('address_detail')

            # 2. التحقق من وجود المستخدم مسبقاً
            user_exists = User.query.filter_by(username=username).first()
            if user_exists:
                return jsonify({
                    'status': 'error', 
                    'message': f'اسم المستخدم "{username}" محجوز مسبقاً.'
                }), 400

            # 3. معالجة رفع صورة الهوية (Identity Image)
            identity_filename = None
            if 'identity_image' in request.files:
                file = request.files['identity_image']
                if file.filename != '':
                    # تأكد من وجود مجلد الرفع: static/uploads/suppliers
                    upload_path = os.path.join(current_app.root_path, 'static/uploads/suppliers')
                    if not os.path.exists(upload_path):
                        os.makedirs(upload_path)
                    
                    filename = secure_filename(f"ID_{username}_{file.filename}")
                    file.save(os.path.join(upload_path, filename))
                    identity_filename = filename

            # 4. إنشاء سجل المستخدم (الحساب البرمجي)
            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                password=hashed_password,
                email=email,
                role='supplier' # تمييز الرتبة في محجوب أونلاين
            )
            db.session.add(new_user)
            db.session.flush() # للحصول على user.id قبل الـ commit النهائي

            # 5. إنشاء سجل بيانات المورد (التفاصيل السيادية)
            new_supplier = Supplier(
                user_id=new_user.id,
                owner_name=owner_name,
                trade_name=trade_name,
                activity_type=activity_type,
                identity_type=identity_type,
                identity_image=identity_filename,
                phone=phone,
                bank_name=bank_name,
                bank_acc=bank_acc,
                province=province,
                district=district,
                address_detail=address_detail
            )
            db.session.add(new_supplier)
            
            # تثبيت العمليات في قاعدة البيانات
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': f'تم تعميد المورد {trade_name} بنجاح في النظام.'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'فشل النظام: {str(e)}'
            }), 500

    # في حالة طلب الصفحة (GET)
    # حساب المعرف القادم لإرساله إلى القالب
    next_id = Supplier.query.count() + 1
    return render_template('admin/add_supplier.html', next_id=next_id)
