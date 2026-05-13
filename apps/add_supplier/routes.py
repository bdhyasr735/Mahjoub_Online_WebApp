import os
from flask import render_template, request, jsonify, url_for, current_app
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

# استيراد كائن قاعدة البيانات والموديلات السيادية
from models.admin_db import db, AdminUser
from models.supplier_db import Supplier

# استيراد البلوبرينت من المجلد الحالي
from . import admin_suppliers

@admin_suppliers.route('/add', methods=['GET', 'POST'])
def add_supplier():
    """
    بوابة إضافة الموردين - محجوب أونلاين
    """
    if request.method == 'POST':
        try:
            # استقبال البيانات السيادية
            username = request.form.get('username')
            password = request.form.get('password')
            trade_name = request.form.get('trade_name')
            owner_name = request.form.get('owner_name')

            # التحقق من عدم تكرار اسم المستخدم في جدول المسؤولين (إذا لزم الأمر)
            exists = AdminUser.query.filter_by(username=username).first()
            if exists:
                return jsonify({'status': 'error', 'message': 'اسم المستخدم محجوز مسبقاً'}), 400

            # أرشفة المورد الجديد في قاعدة البيانات
            new_supplier = Supplier(
                username=username,
                password=generate_password_hash(password),
                trade_name=trade_name,
                owner_name=owner_name,
                # يمكنك إضافة باقي الحقول هنا (الهاتف، البنك، إلخ)
            )
            
            db.session.add(new_supplier)
            db.session.commit()

            return jsonify({'status': 'success', 'message': f'تم تعميد المورد {trade_name} بنجاح'})

        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'فشل النظام: {str(e)}'}), 500

    # عرض واجهة الإضافة وحساب المعرف القادم
    next_id = Supplier.query.count() + 1
    return render_template('admin/add_supplier.html', next_id=next_id)
