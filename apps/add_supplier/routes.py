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
            # 1. استقبال البيانات الأساسية للتحقق
            username = request.form.get('username', '').strip()
            trade_name = request.form.get('trade_name', '').strip()
            password = request.form.get('password')

            # 2. التحقق من التكرار لحماية قاعدة البيانات
            if Supplier.query.filter_by(username=username).first():
                return jsonify({'status': 'error', 'message': 'اسم المستخدم مسجل مسبقاً!'}), 400

            # 3. معالجة حقول الإدخال اليدوي الديناميكية
            
            # أ) نوع الهوية
            identity_type = request.form.get('identity_type')
            if identity_type == 'manual':
                identity_type = request.form.get('manual_identity_type', '').strip()

            # ب) جهة التحويل المالي (بنك أو صرافة)
            bank_name = request.form.get('bank_name')
            if bank_name == 'manual':
                bank_name = request.form.get('manual_bank_name', '').strip()

            # ج) فئة المورد (تم ربطها تحديث لحظي في الـ HTML ولكن للضمان نأخذ القيمة مباشرة)
            category = request.form.get('category', '').strip()

            # 4. إنشاء كائن المورد وحفظ البيانات بداخل الموديل المعتمد لـ Supplier
            hashed_pw = generate_password_hash(password)
            
            new_supplier = Supplier(
                sovereign_id=request.form.get('unified_id'),
                username=username,
                password_hash=hashed_pw,
                identity_type=identity_type,  # القيمة المحددة أو اليدوية
                identity_number=request.form.get('identity_number', '').strip(),
                activity_type=category,       # فئة المورد
                owner_name=request.form.get('owner_name', '').strip(),
                trade_name=trade_name,
                shop_phone=request.form.get('shop_phone', '').strip(),
                province=request.form.get('province'),
                district=request.form.get('district'),
                address_detail=request.form.get('address'),
                fin_type=request.form.get('fin_type'),
                bank_name=bank_name,          # القيمة المحددة أو اليدوية
                bank_acc=request.form.get('bank_acc', '').strip(),
                created_at=datetime.utcnow()
            )

            # 5. معالجة رفع صورة الوثيقة (اختياري - إذا تم رفع ملف)
            # ملاحظة: يمكنك إضافة منطق حفظ الملف على السيرفر هنا إذا كانت قاعدة البيانات تخزن مسار الصورة فقط
            if 'identity_image' in request.files:
                file = request.files['identity_image']
                if file and file.filename != '':
                    # هنا يتم حفظ الملف أو التعامل معه حسب هيكلة المشروع الخاص بك
                    pass

            # 6. الحفظ في قاعدة البيانات عبر SQLAlchemy
            db.session.add(new_supplier)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': 'تم تسجيل وتعميد المورد بنجاح في منظومة محجوب أونلاين ٢٠٢٦'
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'خطأ في النظام الباكيند: {str(e)}'}), 500

    # حساب الرقم التسلسلي القادم تلقائياً لعرضه بصفة لحظية في الواجهة
    try:
        last_s = Supplier.query.order_by(Supplier.id.desc()).first()
        next_id = (last_s.id + 1) if last_s else 1
    except:
        next_id = 1
    
    # استدعاء ملف الـ HTML وتمرير معرف الـ ID التالي
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
