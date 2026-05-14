import os
from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime
from werkzeug.utils import secure_filename

# استيراد مستقر 100% من الملف المحلي الذي أصلحناه معاً
from models.supplier_db import db, Supplier 

# تعريف الـ Blueprint ليعود إلى مجلد القوالب الرئيسي لتلافي أي تضارب
admin_suppliers = Blueprint(
    'admin_suppliers', 
    __name__,
    template_folder='../../templates'
)

# امتدادات الملفات المسموحة لرفع الصور
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- 1. مسار عرض الواجهة واعتماد المورد ---
@admin_suppliers.route('/admin/suppliers/add', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        try:
            # استلام البيانات من النموذج (Form)
            unified_id = request.form.get('unified_id')
            username = request.form.get('username')
            password = request.form.get('password')
            
            category = request.form.get('category')
            if category == 'manual':
                category = request.form.get('manual_category')

            owner_name = request.form.get('owner_name')
            trade_name = request.form.get('trade_name')
            shop_phone = request.form.get('shop_phone')
            
            province = request.form.get('province')
            district = request.form.get('district')
            address_detail = request.form.get('address') # يقرأ من حقل العنوان بالـ HTML

            fin_type = request.form.get('fin_type')
            bank_name = request.form.get('bank_name')
            if bank_name == 'manual':
                bank_name = request.form.get('manual_bank_name')
            bank_acc = request.form.get('bank_acc')

            # حماية لمنع تكرار اسم المستخدم والاسم التجاري
            if Supplier.query.filter_by(username=username).first():
                return jsonify({'status': 'error', 'message': 'اسم المستخدم مسجل مسبقاً!'}), 400
            if Supplier.query.filter_by(trade_name=trade_name).first():
                return jsonify({'status': 'error', 'message': 'الاسم التجاري مسجل مسبقاً!'}), 400

            # بناء السجل وضخ البيانات في جدولك المستقر
            new_supplier = Supplier(
                sovereign_id=unified_id,
                username=username,
                password=password, 
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

            # إرجاع رد النجاح للـ Modal والـ JavaScript
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
                'message': f'حدث خطأ في النظام: {str(e)}'
            }), 500

    # في حالة طلب الـ GET (تحميل الصفحة): حساب الرقم التسلسلي القادم
    try:
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        next_id_num = (last_supplier.id + 1) if last_supplier else 1
    except:
        next_id_num = 1
        
    return render_template('admin/add_supplier.html', next_id=next_id_num)


# --- 2. مسار التحقق اللحظي عبر الـ AJAX منعاً للتكرار ---
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
