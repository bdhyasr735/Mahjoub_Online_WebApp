import os
from flask import render_template, request, jsonify, url_for, current_app, Blueprint
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

# استيراد قاعدة البيانات والموديلات باستخدام المسارات النسبية لتجنب خطأ ModuleNotFoundError
from ..models.admin_db import db  
# ملاحظة: تأكد أن ملف الموديلات يحتوي على كلاس User و Supplier
from ..models.admin_db import User, Supplier 

# تعريف الـ Blueprint الخاص بالموردين
admin_suppliers = Blueprint('admin_suppliers', __name__)

@admin_suppliers.route('/add', methods=['GET', 'POST'])
def add_supplier():
    """
    محرك إضافة الموردين لنظام محجوب أونلاين - متوافق مع Railway و PostgreSQL.
    """
    if request.method == 'POST':
        try:
            # 1. استقبال البيانات من النموذج السيادي
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

            # 2. فحص استباقي لعدم تكرار الهوية الرقمية
            user_exists = User.query.filter_by(username=username).first()
            if user_exists:
                return jsonify({
                    'status': 'error', 
                    'message': f'عذراً، اسم المستخدم "{username}" مسجل بالفعل في قاعدة البيانات.'
                }), 400

            # 3. بروتوكول معالجة صورة الهوية
            identity_filename = None
            if 'identity_image' in request.files:
                file = request.files['identity_image']
                if file and file.filename != '':
                    # تحديد مسار التخزين داخل static
                    upload_folder = os.path.join(current_app.root_path, 'static/uploads/suppliers')
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    
                    filename = secure_filename(f"ID_{username}_{file.filename}")
                    file.save(os.path.join(upload_folder, filename))
                    identity_filename = filename

            # 4. إنشاء الحساب الأساسي (User)
            hashed_pw = generate_password_hash(password)
            new_user = User(
                username=username,
                password=hashed_pw,
                email=email if email else None,
                role='supplier'
            )
            db.session.add(new_user)
            db.session.flush() # الحصول على المعرف قبل الحفظ النهائي

            # 5. أرشفة بيانات المورد (Supplier Profile)
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
            
            # تنفيذ العملية الشاملة
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': f'تم تعميد المورد {trade_name} بنجاح وأرشفة بياناته.'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'فشل في الأرشفة: {str(e)}'
            }), 500

    # عرض واجهة الإضافة (GET)
    # حساب المعرف القادم لعرضه في لوحة التحكم
    next_id = Supplier.query.count() + 1
    return render_template('admin/add_supplier.html', next_id=next_id)
