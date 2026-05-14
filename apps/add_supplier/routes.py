# coding: utf-8
import os
from flask import render_template, request, jsonify, current_app, Blueprint
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

# استيراد كائن قاعدة البيانات والموديلات لضمان وحدة البيانات السيادية
from models.admin_db import db, AdminUser
from models.supplier_db import Supplier

# تعريف الـ Blueprint الخاص بإدارة الموردين
admin_suppliers = Blueprint(
    'admin_suppliers', 
    __name__, 
    template_folder='templates'
)

# إعدادات أمان رفع الملفات لصور الهوية والوثائق
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    """التحقق من امتداد الملف لضمان أمن النظام"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_suppliers.route('/check-duplicate/', methods=['GET'])
def check_duplicate():
    """
    نظام التحقق الفوري (AJAX) لمنع التكرار قبل الحفظ
    تم تحديثه ليشمل رقم هاتف المحل
    """
    field_type = request.args.get('type')
    value = request.args.get('value')
    
    if not field_type or not value:
        return jsonify({'exists': False})

    exists = False
    
    if field_type == 'username':
        exists = AdminUser.query.filter_by(username=value).first() is not None or \
                 Supplier.query.filter_by(username=value).first() is not None
    
    elif field_type == 'owner_phone':
        exists = Supplier.query.filter_by(owner_phone=value).first() is not None
        
    elif field_type == 'shop_phone':
        # التحقق من عدم تكرار رقم هاتف المنشأة
        exists = Supplier.query.filter_by(shop_phone=value).first() is not None
        
    elif field_type == 'trade_name':
        exists = Supplier.query.filter_by(trade_name=value).first() is not None
        
    elif field_type == 'owner_name':
        exists = Supplier.query.filter_by(owner_name=value).first() is not None

    return jsonify({'exists': exists})

@admin_suppliers.route('/add', methods=['GET', 'POST'])
def add_supplier():
    """
    محرك تعميد الموردين - منظومة محجوب أونلاين السيادية
    تم إصلاح منطق الاستجابة لضمان ظهور رسالة النجاح في الـ Frontend
    """
    if request.method == 'POST':
        try:
            # 1. استقبال البيانات الأساسية
            unified_id = request.form.get('unified_id')
            username = request.form.get('username')
            password = request.form.get('password') 
            
            # 2. بيانات النشاط والاتصال
            category = request.form.get('category')
            owner_name = request.form.get('owner_name')
            trade_name = request.form.get('trade_name')
            owner_phone = request.form.get('owner_phone')
            shop_phone = request.form.get('shop_phone') # الحقل المضاف
            
            # 3. التوزيع الجغرافي والمالي
            province = request.form.get('province')
            district = request.form.get('district')
            fin_type = request.form.get('fin_type')
            bank_name = request.form.get('bank_name')
            bank_acc = request.form.get('bank_acc')

            # --- 4. الفحص الأمني المزدوج (Server-side) ---
            if Supplier.query.filter_by(username=username).first():
                return jsonify({'status': 'error', 'message': 'اسم المستخدم مسجل مسبقاً.'}), 200
            
            if Supplier.query.filter_by(shop_phone=shop_phone).first():
                return jsonify({'status': 'error', 'message': 'رقم هاتف المنشأة مسجل لمورد آخر.'}), 200

            # --- 5. معالجة الصور ---
            identity_image_path = None
            file = request.files.get('identity_image')
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{unified_id}_{file.filename}")
                upload_path = os.path.join(current_app.root_path, 'static/uploads/suppliers/ids')
                
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                
                file.save(os.path.join(upload_path, filename))
                identity_image_path = f"uploads/suppliers/ids/{filename}"

            # --- 6. إنشاء السجل وحفظه ---
            new_supplier = Supplier(
                sovereign_id=unified_id,
                username=username,
                password=generate_password_hash(password),
                activity_type=category,
                identity_image=identity_image_path,
                owner_name=owner_name,
                trade_name=trade_name,
                owner_phone=owner_phone,
                shop_phone=shop_phone,
                province=province,
                district=district,
                fin_type=fin_type,
                bank_name=bank_name,
                bank_acc=bank_acc,
                is_active=True
            )

            db.session.add(new_supplier)
            db.session.commit()

            # --- 7. رد النجاح الحاسم (هذا ما ينتظره الـ JavaScript) ---
            return jsonify({
                'status': 'success', 
                'message': 'تم الاعتماد بنجاح',
                'data': {
                    'username': username,
                    'password': password, # نرسل كلمة السر الصافية للعرض فقط في المودال
                    'trade_name': trade_name,
                    'unified_id': unified_id
                }
            })

        except Exception as e:
            db.session.rollback()
            # تسجيل الخطأ في السيرفر للمراجعة
            print(f"Error in add_supplier: {str(e)}") 
            return jsonify({
                'status': 'error', 
                'message': f'حدث خطأ تقني: {str(e)}'
            }), 500

    # معالجة طلب GET لعرض الصفحة
    try:
        next_id = Supplier.query.count() + 1
    except:
        next_id = 1
        
    return render_template('admin/add_supplier.html', next_id=next_id)
