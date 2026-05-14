import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required  # 🛡️ استيراد جدار حماية الدخول
from datetime import datetime
from apps import db  
from models.supplier_db import Supplier 

# إعداد المسارات الديناميكية للقوالب
current_dir = os.path.dirname(os.path.abspath(__file__))
global_template_dir = os.path.abspath(os.path.join(current_dir, '..', 'templates'))

admin_suppliers = Blueprint(
    'admin_suppliers', 
    __name__,
    template_folder=global_template_dir
)

@admin_suppliers.route('/add', methods=['GET', 'POST'])
@login_required  # 🛡️ تأمين الرابط: لا يمكن الدخول إلا للمسجلين في النظام
def add_supplier():
    # الأمان السيادي: فحص وإنشاء الجدول فوراً عند طلب الصفحة
    try:
        db.create_all()
    except Exception as e:
        print(f"⚠️ DB create failed or exists: {e}")

    if request.method == 'POST':
        try:
            # 1. استقبال البيانات من نموذج الإضافة
            unified_id = request.form.get('unified_id')
            username = request.form.get('username', '').strip()
            password = request.form.get('password')
            
            category = request.form.get('category')
            business_type = request.form.get('business_type')
            owner_name = request.form.get('owner_name', '').strip()
            trade_name = request.form.get('trade_name', '').strip()
            shop_phone = request.form.get('shop_phone', '').strip()
            
            province = request.form.get('province')
            district = request.form.get('district')
            address_detail = request.form.get('address') 

            fin_type = request.form.get('fin_type')
            bank_name = request.form.get('bank_name')
            if bank_name == 'manual':
                bank_name = request.form.get('manual_bank_name')
            bank_acc = request.form.get('bank_acc', '').strip()

            # 2. جدار الحماية النهائي في الباك إند (تأكيد عدم التكرار)
            if Supplier.query.filter_by(username=username).first():
                return jsonify({'status': 'error', 'message': 'عذراً، اسم المستخدم مسجل مسبقاً!'}), 400
            
            if Supplier.query.filter_by(trade_name=trade_name).first():
                return jsonify({'status': 'error', 'message': 'عذراً، الاسم التجاري للمنشأة مسجل مسبقاً!'}), 400

            # 3. إنشاء كائن المورد الجديد
            new_supplier = Supplier(
                sovereign_id=unified_id,
                username=username,
                password=password, # ملاحظة: يفضل تشفير كلمة المرور في مراحل لاحقة
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

            # إضافة نوع النشاط إذا كان العمود موجوداً في الموديل
            if hasattr(Supplier, 'business_type'):
                new_supplier.business_type = business_type

            # 4. الحفظ في قاعدة البيانات
            db.session.add(new_supplier)
            db.session.commit()

            # 5. العودة ببيانات النجاح لعرضها في النافذة المنبثقة (Modal)
            return jsonify({
                'status': 'success',
                'data': {
                    'username': username,
                    'password': password,
                    'owner_name': owner_name,
                    'trade_name': trade_name
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'حدث خطأ في الخادم: {str(e)}'}), 500

    # حساب الرقم التسلسلي القادم (ID)
    next_id_num = 1
    try:
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        if last_supplier:
            next_id_num = last_supplier.id + 1
    except Exception:
        next_id_num = 1
        
    return render_template('admin/add_supplier.html', next_id=next_id_num)


@admin_suppliers.route('/check-duplicate', methods=['GET'])
@login_required # تأمين مسار الفحص أيضاً
def check_duplicate():
    """ 🌟 محرك الفحص اللحظي المحدث لمنع التكرار """
    check_type = request.args.get('type')
    value = request.args.get('value', '').strip()

    if not check_type or not value:
        return jsonify({'exists': False})

    exists = False
    try:
        # فحص الحقول المختلفة بناءً على النوع المرسل من JavaScript
        if check_type == 'username':
            exists = Supplier.query.filter_by(username=value).first() is not None
        elif check_type == 'trade_name':
            exists = Supplier.query.filter_by(trade_name=value).first() is not None
        elif check_type == 'owner_name':
            exists = Supplier.query.filter_by(owner_name=value).first() is not None
        elif check_type == 'shop_phone':
            exists = Supplier.query.filter_by(shop_phone=value).first() is not None
        elif check_type == 'bank_acc':
            exists = Supplier.query.filter_by(bank_account=value).first() is not None
            
    except Exception as e:
        print(f"Validation error: {e}")
        exists = False

    return jsonify({'exists': exists})
