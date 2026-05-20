# coding: utf-8
# 🏢 مسارات تعميد وأرشفة الموردين السيادية - منصة محجوب أونلاين 2026

import os
import uuid
import re
from flask import Blueprint, request, jsonify, render_template, url_for, current_app
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

# استيراد كائن db الموحد لمنع التعارض الدائري (Circular Import)
from apps import db 

admin_suppliers_bp = Blueprint('add_supplier', __name__, template_folder='templates')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_next_sequence_codes():
    """توليد الكود التسلسلي التالي للمورد بشكل ديناميكي من قاعدة البيانات"""
    from apps.models.supplier_db import Supplier
    try:
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        if last_supplier and last_supplier.sovereign_id:
            # معالجة الرقم الموجود في السلسلة
            match = re.search(r'\d+', last_supplier.sovereign_id)
            if match:
                next_num = int(match.group()) + 1
                return f"SUP-MAH{next_num}"
        return "SUP-MAH9631"
    except Exception as e:
        current_app.logger.error(f"❌ خطأ أثناء توليد التسلسل: {str(e)}")
        return "SUP-MAH9631"

@admin_suppliers_bp.route('/admin/suppliers/check-duplicate', methods=['GET'])
def check_duplicate():
    from apps.models.supplier_db import Supplier
    
    check_type = request.args.get('type')
    value = request.args.get('value', '').strip()

    if check_type == 'get_next_sequence':
        next_sup = generate_next_sequence_codes()
        return jsonify({'next_sequence': next_sup})

    if not value:
        return jsonify({'exists': False})

    exists = False
    # التحقق من وجود القيمة في قاعدة البيانات باستخدام عبارة exists()
    try:
        if check_type == 'username':
            exists = db.session.query(Supplier.query.filter_by(username=value).exists()).scalar()
        elif check_type == 'identity_number':
            exists = db.session.query(Supplier.query.filter_by(identity_number=value).exists()).scalar()
        # إضافة باقي الفحوصات...
    except Exception:
        exists = False
        
    return jsonify({'exists': exists})

@admin_suppliers_bp.route('/admin/suppliers/add', methods=['GET', 'POST'])
def add_supplier_submit():
    if request.method == 'GET':
        return render_template('admin/add_supplier.html')

    from apps.models.supplier_db import Supplier
    from apps.models.wallet_db import Wallet

    try:
        # استخراج البيانات مع تأمين ضد القيم الفارغة
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        identity_type = request.form.get('identity_type', 'هوية وطنية')
        identity_number = request.form.get('identity_number', '').strip()
        
        # حماية: التحقق من وجود كلمة مرور
        if not password:
            return jsonify({'status': 'error', 'message': 'كلمة المرور مطلوبة'}), 400

        # توليد المعرفات
        final_sovereign_id = generate_next_sequence_codes()
        final_wallet_code = final_sovereign_id.replace("SUP-", "WEL-", 1)

        # حفظ الصورة (معالجة الملفات)
        identity_image_path = None
        if 'identity_image' in request.files:
            file = request.files['identity_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"doc_{uuid.uuid4().hex[:8]}_{filename}"
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/identities')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                file.save(os.path.join(upload_folder, unique_filename))
                identity_image_path = os.path.join(upload_folder, unique_filename)

        # الحفظ في قاعدة البيانات
        hashed_pwd = generate_password_hash(password)
        new_supplier = Supplier(
            sovereign_id=final_sovereign_id,
            wallet_code=final_wallet_code,
            username=username,
            password_hash=hashed_pwd,
            identity_type=identity_type,
            identity_number=identity_number,
            identity_image=identity_image_path,
            owner_name=request.form.get('owner_name', ''),
            trade_name=request.form.get('trade_name', ''),
            owner_phone=request.form.get('owner_phone', ''),
            status='active'
        )
        
        db.session.add(new_supplier)
        db.session.flush()

        new_wallet = Wallet(supplier_id=final_sovereign_id, wallet_code=final_wallet_code, status='نشطة')
        db.session.add(new_wallet)
        
        db.session.commit()

        return jsonify({
            'status': 'success',
            'redirect_url': url_for('add_supplier.admin_suppliers_list')
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ خطأ الحفظ: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_suppliers_bp.route('/admin/suppliers/list')
def admin_suppliers_list():
    return render_template('admin_suppliers_list.html')
