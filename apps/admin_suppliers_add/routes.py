# coding: utf-8
# 📂 apps/admin_suppliers_add/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from apps.models.supplier_db import Supplier
from apps.extensions import db
import logging

# تعريف البلوبرينت
admin_suppliers_add_bp = Blueprint(
    'admin_suppliers_add', 
    __name__, 
    template_folder='templates'
)

@admin_suppliers_add_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        try:
            # 1. استقبال البيانات
            username = request.form.get('username')
            trade_name = request.form.get('trade_name')
            phone = request.form.get('phone')
            password = request.form.get('password')

            # 2. التحقق من البيانات
            if not username or not password:
                flash("يرجى تعبئة كافة الحقول المطلوبة", "danger")
                return redirect(url_for('admin_suppliers_add.add_supplier'))

            # 3. التحقق من وجود المورد
            if Supplier.query.filter_by(username=username).first():
                flash("اسم المستخدم موجود مسبقاً!", "danger")
                return redirect(url_for('admin_suppliers_add.add_supplier'))

            # 4. إنشاء وحفظ المورد
            new_supplier = Supplier(
                username=username, 
                trade_name=trade_name, 
                status='active'
            )
            new_supplier.phone = phone
            new_supplier.set_password(password)
            
            db.session.add(new_supplier)
            db.session.commit()
            
            flash(f"تم إضافة الشريك {trade_name} بنجاح!", "success")
            return redirect(url_for('admin_suppliers_add.add_supplier'))

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding supplier: {str(e)}")
            flash(f"حدث خطأ أثناء الحفظ: {str(e)}", "danger")
            return redirect(url_for('admin_suppliers_add.add_supplier'))
        
    # عرض الصفحة
    return render_template('admin_suppliers_add/admin_suppliers_add.html')
