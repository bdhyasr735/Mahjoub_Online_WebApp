import os
from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from apps import db  # استيراد كائن قاعدة البيانات المركزي المشترك
from models.supplier_db import Supplier # استيراد موديل الموردين

# 🎯 تفعيل المسار الداخلي الصارم: جعل الـ Blueprint يقرأ مجلد templates الموجود بجانبه مباشرة
current_dir = os.path.dirname(os.path.abspath(__file__))
local_template_dir = os.path.join(current_dir, 'templates')

admin_suppliers = Blueprint(
    'admin_suppliers', 
    __name__,
    template_folder=local_template_dir
)

# 🔥 التوليد التلقائي المستقل: إنشاء الجدول فوراً عند قراءة الحزمة في السيرفر
with admin_suppliers.record_once(lambda state: None):
    try:
        from run import create_app
        app = create_app()
        with app.app_context():
            db.create_all()
            print("🚀 [Independent DB] 'suppliers' table created successfully or already exists!")
    except Exception as e:
        print(f"⚠️ Initial DB setup skipped, will retry inside route: {e}")


@admin_suppliers.route('/add', methods=['GET', 'POST'])
def add_supplier():
    # خطة دفاعية ثنائية: التأكد من وجود الجدول فور طلب الصفحة
    try:
        db.create_all()
    except Exception:
        pass

    if request.method == 'POST':
        try:
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
            address_detail = request.form.get('address') 

            fin_type = request.form.get('fin_type')
            bank_name = request.form.get('bank_name')
            if bank_name == 'manual':
                bank_name = request.form.get('manual_bank_name')
            bank_acc = request.form.get('bank_acc')

            # فحص ومنع تكرار البيانات قبل الحفظ والتسبب في خطأ قاعدة البيانات
            if Supplier.query.filter_by(username=username).first():
                return jsonify({'status': 'error', 'message': 'اسم المستخدم مسجل مسبقاً!'}), 400
            if Supplier.query.filter_by(trade_name=trade_name).first():
                return jsonify({'status': 'error', 'message': 'الاسم التجاري مسجل مسبقاً!'}), 400

            # إنشاء كائن المورد الجديد بالأعمدة المحدثة
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
            return jsonify({'status': 'error', 'message': f'حدث خطأ في الخادم: {str(e)}'}), 500

    # حساب المعرّف التسلسلي التالي تلقائياً لعرضه في الواجهة
    next_id_num = 1
    try:
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        if last_supplier:
            next_id_num = last_supplier.id + 1
    except Exception as e:
        next_id_num = 1
        
    return render_template('admin/add_supplier.html', next_id=next_id_num, next_id_num=next_id_num)


@admin_suppliers.route('/check-duplicate', methods=['GET'])
def check_duplicate():
    check_type = request.args.get('type')
    value = request.args.get('value', '').strip()
    bank_name = request.args.get('bank_name', '').strip()

    if not check_type or not value:
        return jsonify({'exists': False})

    exists = False
    try:
        if check_type == 'username':
            exists = Supplier.query.filter_by(username=value).first() is not None
        elif check_type == 'trade_name':
            exists = Supplier.query.filter_by(trade_name=value).first() is not None
        elif check_type == 'shop_phone':
            exists = Supplier.query.filter_by(shop_phone=value).first() is not None
        elif check_type == 'bank_acc':
            exists = Supplier.query.filter_by(bank_account=value, bank_name=bank_name).first() is not None
    except Exception:
        exists = False

    return jsonify({'exists': exists})
