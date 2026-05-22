from flask import Blueprint, request, jsonify, render_code, url_for # حسب مكاتبك الحالية
from apps.extensions import db # أو مسار استدعاء الـ db عندك
from apps.models import Supplier # أو اسم الكلاس المسؤول عن جدول الموردين في الداتابيز

# دالة توليد الأرقام المتسلسلة التلقائية لـ (المورد والمحفظة)
@add_supplier.route('/check_duplicate', methods=['GET'])
def check_duplicate():
    check_type = request.args.get('type')
    
    # 1. جلب التسلسل التلقائي الذكي المعتمد لمنصة محجوب أونلاين
    if check_type == 'get_next_sequence':
        try:
            # استعلام لجلب آخر مورد مضاف بناءً على الـ ID التلقائي
            last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
            
            if last_supplier and last_supplier.supplier_id:
                # إزالة الجزء الثابت واستخراج الرقم المتسلسل الأساسي
                prefix = "SUP-MAH963"
                last_num_str = last_supplier.supplier_id[len(prefix):]
                
                if last_num_str.isdigit():
                    next_number = int(last_num_str) + 1
                else:
                    next_number = 1
            else:
                next_number = 1 # إذا كانت الداتابيز فارغة تماماً
                
            # بناء المعرفات الموحدة المتناسقة مع قاعدة البيانات الحية
            next_supplier_id = f"SUP-MAH963{next_number}"
            next_wallet_id = f"WEL-MAH963{next_number}"
            
            return jsonify({
                "next_sequence": next_supplier_id,
                "next_wallet": next_wallet_id
            })
            
        except Exception as e:
            # صمام أمان لضمان عدم توقف العمل عند أي مشكلة طارئة
            return jsonify({"next_sequence": "SUP-MAH9631", "next_wallet": "WEL-MAH9631"})
            
    # ... بقية التحققات الخاصة بالـ username أو identity_number إذا كانت موجودة لديك ...


# دالة استقبال الفورم وحفظ البيانات (بما فيها رقم المحل المتناسق)
@add_supplier.route('/add_supplier_submit', methods=['POST'])
def add_supplier_submit():
    try:
        # استقبال البيانات من الفورم الـ HTML المحدث
        supplier_id = request.form.get('sovereign_id')   # القادم من حقل hidden المخفي
        wallet_code = request.form.get('wallet_code')   # القادم من حقل hidden المخفي
        
        username = request.form.get('username')
        password = request.form.get('password') # تأكد من عمل hashing لها إذا لزم الأمر
        identity_type = request.form.get('identity_type')
        identity_number = request.form.get('identity_number')
        
        owner_name = request.form.get('owner_name')
        trade_name = request.form.get('trade_name')
        shop_number = request.form.get('shop_number') # <--- الحقل الجديد المستلم من الواجهة!
        owner_phone = request.form.get('owner_phone')
        province = request.form.get('province')
        district = request.form.get('district')
        address_detail = request.form.get('address_detail')
        
        bank_name = request.form.get('bank_name')
        bank_acc = request.form.get('bank_acc')

        # معالجة ملف الصورة لو تم رفعه
        # identity_image = request.files.get('identity_image')

        # إنشاء كائن المورد الجديد وإدراج البيانات به
        new_supplier = Supplier(
            supplier_id=supplier_id,
            wallet_code=wallet_code,
            username=username,
            password=password,
            identity_type=identity_type,
            identity_number=identity_number,
            owner_name=owner_name,
            trade_name=trade_name,
            shop_number=shop_number, # <--- تأكد أن هذا العمود مضاف في كلاس الـ Model بالداتابيز
            owner_phone=owner_phone,
            province=province,
            district=district,
            address_detail=address_detail,
            bank_name=bank_name,
            bank_acc=bank_acc
        )
        
        db.session.add(new_supplier)
        db.session.commit()
        
        return jsonify({"status": "success", "message": "تم تعميد المورد بنجاح"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)})
