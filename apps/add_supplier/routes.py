import os
from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime
from werkzeug.utils import secure_filename

# الاستيراد المستقر والمضمون الذي لا يفصل السيرفر
from models.supplier_db import db, Supplier 

# تعريف الـ Blueprint بناءً على المسار المعتمد لديك
admin_suppliers = Blueprint(
    'admin_suppliers', 
    __name__,
    template_folder='../../templates' # يشير لمجلد القوالب الرئيسي كما هو في كودك الشغال
)

# امتدادات الصور المسموحة
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- 1. مسار عرض الواجهة واعتماد المورد ---
@admin_suppliers.route('/admin/suppliers/add', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        try:
            # أ. استلام البيانات من النموذج (Form)
            unified_id = request.form.get('unified_id')
            username = request.form.get('username')
            password = request.form.get('password')
            
            # ب. معالجة الفئة
            category = request.form.get('category')
            if category == 'manual':
                category = request.form.get('manual_category')

            owner_name = request.form.get('owner_name')
            trade_name = request.form.get('trade_name')
            shop_phone = request.form.get('shop_phone')
            
            province = request.form.get('province')
            district = request.form.get('district')
            address_detail = request.form.get('address') # متوافق مع name="address" في الـ HTML

            # ج. معالجة الربط المالي والجهات اليدوية
            fin_type = request.form.get('fin_type')
            bank_name = request.form.get('bank_name')
            if bank_name == 'manual':
                bank_name = request.form.get('manual_bank_name')
            bank_acc = request.form.get('bank_acc')

            # د. التحقق المسبق الذكي لمنع التكرار (حتى لا تظهر أخطاء SQL غامضة)
            if Supplier.query.filter_by(username=username).first():
                return jsonify({'status': 'error', 'message': 'اسم المستخدم مسجل مسبقاً!'}), 400
            if Supplier.query.filter_by(trade_name=trade_name).first():
                return jsonify({'status': 'error', 'message': 'الاسم التجاري مسجل مسبقاً!'}), 400

            # هـ. معالجة ورفع صورة الهوية (إضافة حماية للملفات)
            file = request.files.get('identity_image')
            filename = None
            if file and allowed_file(file.filename):
                clean_filename = secure_filename(file.filename)
                filename = f"{unified_id}_{clean_filename}"
                upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'suppliers_ids')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                file.save(os.path.join(upload_path, filename))

            # و. إنشاء السجل وضخ البيانات في الحقول المطابقة لقاعدة بياناتك المستقرة
            new_supplier = Supplier(
                sovereign_id=unified_id,
                username=username,
                password=password, # يتطابق مع الحقل الحالي في الموديل الخاص بك
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
                created_at=datetime.utcnow()
            )

            db.session.add(new_supplier)
            db.session.commit()

            # ز. إرجاع الرد المتوافق 100% مع الـ Modal في قالب الـ HTML ليظهر بنجاح
            return jsonify({
                'status': 'success',
                'data': {
                    'sovereign_id': unified_id,
                    'username': username,
                    'password': password
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'حدث خطأ أثناء الحفظ: {str(e)}'
            }), 500

    # في حالة طلب الـ GET: حساب المعرف القادم بأمان
    try:
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        next_id_num = (last_supplier.id + 1) if last_supplier else 1
    except:
        next_id_num = 1
        
    return render_template('admin/add_supplier.html', next_id=next_id_num)


# --- 2. إضافة مسار نظام التحقق اللحظي (Ajax Validation) بدون أي تضارب ---
@admin_suppliers.route('/admin/suppliers/check-duplicate', methods=['GET'])
def check_duplicate():
    check_type = request.args.get('type')
    value = request.args.get('value', '').strip()
    bank_name = request.args.get('bank_name', '').strip()

    if not check_type or not value:
        return jsonify({'exists': False})

    exists = False

    if check_type == 'username':
        exists = Supplier.query.filter_by(username=value).first() is not None
    
    elif check_type == 'trade_name':
        exists = Supplier.query.filter_by(trade_name=value).first() is not None

    elif check_type == 'shop_phone':
        exists = Supplier.query.filter_by(shop_phone=value).first() is not None

    elif check_type == 'bank_acc':
        exists = Supplier.query.filter_by(bank_account=value, bank_name=bank_name).first() is not None

    return jsonify({'exists': exists})
