import json
from flask import Blueprint, render_template, request, jsonify
from cryptography.fernet import Fernet # المكتبة الموصى بها لـ AES
from .models import db, Supplier, SupplierCategory # افترض وجود هذه النماذج

# إعداد الـ Blueprint والتشفير
add_supplier = Blueprint('add_supplier', __name__, template_folder='templates')
# في بيئة الإنتاج، ضع هذا المفتاح في ملف .env
CIPHER_KEY = Fernet.generate_key() 
cipher_suite = Fernet(CIPHER_KEY)

@add_supplier.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier_page():
    return render_template('admin/add_supplier.html')

@add_supplier.route('/add_supplier_submit', methods=['POST'])
def add_supplier_submit():
    try:
        # 1. استلام البيانات المشفرة من النموذج
        encrypted_payload = request.form.get('encrypted_payload')
        
        # 2. فك التشفير (ملاحظة: إذا كنت تستخدم CryptoJS، تأكد من توافق التشفير)
        # هنا سنستخدم نموذج مبسط لفك التشفير
        decrypted_data = cipher_suite.decrypt(encrypted_payload.encode()).decode()
        data = json.loads(decrypted_data)
        
        # 3. معالجة البيانات وتخزينها
        new_supplier = Supplier(
            username=data['username'],
            owner_name=data['owner_name'],
            trade_name=data['trade_name'],
            category=data['category'],
            # ... باقي الحقول
        )
        db.session.add(new_supplier)
        db.session.commit()
        
        return jsonify({"status": "success", "message": "تم تعميد المورد بنجاح"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@add_supplier.route('/save_new_option', methods=['POST'])
def save_new_option():
    """هذا هو محرك التعلم الذاتي للحقول"""
    data = request.json
    field_name = data.get('field') # مثال: 'categorySelect'
    new_value = data.get('value')
    
    # التحقق من عدم التكرار في قاعدة البيانات
    existing = SupplierCategory.query.filter_by(name=new_value).first()
    if not existing:
        new_cat = SupplierCategory(name=new_value, field_type=field_name)
        db.session.add(new_cat)
        db.session.commit()
        return jsonify({"status": "success", "added": new_value})
    
    return jsonify({"status": "exists"}), 200

@add_supplier.route('/check_duplicate', methods=['GET'])
def check_duplicate():
    """محرك التحقق اللحظي"""
    check_type = request.args.get('type')
    value = request.args.get('value')
    
    # مثال منطق التحقق
    exists = Supplier.query.filter_by(**{check_type: value}).first()
    return jsonify({"available": exists is None})
