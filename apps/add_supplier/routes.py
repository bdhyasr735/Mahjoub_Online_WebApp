# coding: utf-8
import os
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from datetime import datetime
from werkzeug.security import generate_password_hash

# 🚀 استيراد قاعدة البيانات والموديل بمسارات مطلقة لضمان العمل على Linux/Railway
from apps import db  
from apps.models.supplier_db import Supplier 

# إعداد الـ Blueprint مع تحديد مسار القوالب بدقة
# استخدام os.path لضمان أن Flask يجد مجلد templates مهما كان مكان تشغيل السيرفر
current_dir = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(current_dir, 'templates')

admin_suppliers = Blueprint(
    'admin_suppliers', 
    __name__,
    template_folder=template_path  # تحديد المسار الكامل للمجلد
)

@admin_suppliers.route('/add', methods=['GET', 'POST'])
@login_required 
def add_supplier():
    if request.method == 'POST':
        try:
            # 1. استقبال البيانات
            username = request.form.get('username', '').strip()
            password = request.form.get('password')
            trade_name = request.form.get('trade_name', '').strip()

            # 2. التحقق من التكرار
            if Supplier.query.filter_by(username=username).first():
                return jsonify({'status': 'error', 'message': 'اسم المستخدم مسجل مسبقاً!'}), 400

            # 3. إنشاء كائن المورد
            hashed_pw = generate_password_hash(password)
            
            new_supplier = Supplier(
                sovereign_id=request.form.get('unified_id'),
                username=username,
                password_hash=hashed_pw, # تأكد أن اسم الحقل في الموديل هو password_hash
                activity_type=request.form.get('category'), # تأكد من مطابقة الأسماء مع الموديل
                owner_name=request.form.get('owner_name', '').strip(),
                trade_name=trade_name,
                shop_phone=request.form.get('shop_phone', '').strip(),
                province=request.form.get('province'),
                district=request.form.get('district'),
                address_detail=request.form.get('address'),
                fin_type=request.form.get('fin_type'),
                bank_name=request.form.get('bank_name'),
                bank_acc=request.form.get('bank_acc', '').strip(),
                created_at=datetime.utcnow()
            )

            # 4. الحفظ
            db.session.add(new_supplier)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': 'تم تسجيل المورد بنجاح في منظومة محجوب أونلاين'
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'خطأ في النظام: {str(e)}'}), 500

    # حساب الرقم التسلسلي القادم لعرضه في الواجهة
    try:
        last_s = Supplier.query.order_by(Supplier.id.desc()).first()
        next_id = (last_s.id + 1) if last_s else 1
    except:
        next_id = 1
    
    # تأكد أن الملف موجود في apps/add_supplier/templates/admin/add_supplier.html
    return render_template('admin/add_supplier.html', next_id=next_id)

@admin_suppliers.route('/check-duplicate', methods=['GET'])
@login_required
def check_duplicate():
    check_type = request.args.get('type')
    value = request.args.get('value', '').strip()

    if not check_type or not value:
        return jsonify({'exists': False})

    fields = {
        'username': Supplier.username,
        'trade_name': Supplier.trade_name,
        'shop_phone': Supplier.shop_phone
    }

    field = fields.get(check_type)
    exists = False
    if field:
        exists = Supplier.query.filter(field == value).first() is not None

    return jsonify({'exists': exists})
