# coding: utf-8
from flask import Blueprint, request, jsonify, render_template
from apps.extensions import db
from apps.models.supplier import Supplier
from apps.utils.security import AESCipher
import os

# تعريف الـ Blueprint
add_supplier = Blueprint('add_supplier', __name__)

# تهيئة المشفر بنفس المفتاح الموجود في الموديل
cipher = AESCipher(os.getenv('ENCRYPTION_KEY', 'your-32-byte-key-here-must-be-secure'))

@add_supplier.route('/add', methods=['GET', 'POST'])
def add_supplier_submit():
    if request.method == 'GET':
        return render_template('add_supplier.html')

    # استقبال البيانات المشفرة بصيغة JSON
    data = request.get_json()

    try:
        # إنشاء المورد الجديد
        # الموديل سيقوم بفك التشفير عند الاسترجاع (Properties) 
        # وإعادة التشفير عند الحفظ (Setters) تلقائياً
        new_supplier = Supplier(
            sovereign_id = f"SUP-MHA_{os.urandom(4).hex()}", # توليد معرف فريد
            wallet_code = os.urandom(8).hex(),
            owner_name = data['owner_name'],
            owner_phone = data['phone'],
            trade_name = data['trade_name'],
            shop_phone = data['phone'], # نفترض مطابقة الهاتف للآن
            bank_acc = data['bank_acc'],
            username = data['username'],
            password_hash = data['password'], # يفضل عمل Hashing هنا
            identity_type = 'بطاقة شخصية',
            identity_number = data['identity_number'],
            activity_type = data['activity_type'],
            bank_name = data['bank_name'],
            province = data.get('province'),
            district = data.get('district'),
            address_detail = data.get('address_detail')
        )
        
        db.session.add(new_supplier)
        db.session.commit()
        
        return jsonify({"status": "success", "message": "تمت أرشفة المورد بنجاح في سجلات محجوب أونلاين"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400

# مسار الاستدعاء اللحظي للتحقق من عدم تكرار البيانات
@add_supplier.route('/api/check_unique', methods=['GET'])
def check_unique():
    field = request.args.get('field')
    value = request.args.get('value')
    
    if not field or not value:
        return jsonify({"exists": False})

    # التحقق في قاعدة البيانات
    exists = Supplier.query.filter(getattr(Supplier, field) == value).first() is not None
    
    return jsonify({"exists": exists})
