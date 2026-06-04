# coding: utf-8
# 📂 apps/add_supplier/routes.py

import os
from flask import render_template, request, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from apps.add_supplier import add_supplier_bp
from apps.models.supplier_db import Supplier
from apps.extensions import db
from apps.config import constants
from datetime import datetime

# إعداد مسار حفظ الصور (تأكد من وجود المجلد)
UPLOAD_FOLDER = 'apps/static/uploads/identities'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@add_supplier_bp.route('/add', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'GET':
        # تمرير الثوابت للقالب
        return render_template('admin/add_supplier.html', constants=constants, next_id="963")

    if request.method == 'POST':
        try:
            # 1. استقبال البيانات من نموذج الـ FormData
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                return jsonify({"status": "error", "message": "بيانات الدخول الأساسية ناقصة"}), 400

            # 2. معالجة صورة الهوية (اختياري)
            identity_image = request.files.get('identity_image')
            image_path = None
            if identity_image:
                filename = secure_filename(f"{username}_{datetime.now().strftime('%Y%m%d')}_{identity_image.filename}")
                identity_image.save(os.path.join(UPLOAD_FOLDER, filename))
                image_path = filename

            # 3. إنشاء المورد الجديد
            # ملاحظة: التشفير يتم تلقائياً عبر الـ setters في نموذج Supplier
            new_supplier = Supplier(
                username=username,
                password_hash=generate_password_hash(password),
                sovereign_id=f"SUP-MHA_963{request.form.get('next_id', '000')}",
                trade_name=request.form.get('trade_name'),
                owner_name=request.form.get('owner_name'),
                id_type=request.form.get('identity_type'),
                supply_category=request.form.get('activity_type'),
                owner_phone=request.form.get('phone'),
                shop_phone=request.form.get('phone'), 
                province=request.form.get('province'),
                district=request.form.get('district'),
                address_detail=request.form.get('address_detail'),
                bank_name=request.form.get('bank_name'),
                bank_acc=request.form.get('bank_acc')
            )
            
            # 4. الحفظ في قاعدة البيانات
            db.session.add(new_supplier)
            db.session.commit()
            
            return jsonify({
                "status": "success", 
                "message": "تمت الأرشفة السيادية بنجاح وتشفير كافة البيانات"
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saving supplier: {e}")
            return jsonify({"status": "error", "message": "حدث خطأ أثناء الاتصال بالخزينة المركزية"}), 400
