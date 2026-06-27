# 📂 apps/suppliers_add/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from apps.models.supplier_db import Supplier
from apps.extensions import db
import logging

# إعداد المسارات والقوالب
suppliers_add_bp = Blueprint(
    'suppliers_add', 
    __name__, 
    template_folder='templates'
)

@suppliers_add_bp.route('/add', methods=['GET', 'POST'])
@login_required 
def add_supplier():
    if request.method == 'POST':
        try:
            # 1. استقبال البيانات
            username = request.form.get('username')
            trade_name = request.form.get('trade_name')
            phone = request.form.get('phone')
            password = request.form.get('password')

            # 2. التحقق الأساسي
            if not username or not password:
                flash("اسم المستخدم وكلمة المرور حقول مطلوبة", "danger")
                return redirect(url_for('suppliers_add.add_supplier'))

            # 3. التحقق من التكرار
            if Supplier.query.filter_by(username=username).first():
                flash("اسم المستخدم موجود مسبقاً!", "danger")
                return redirect(url_for('suppliers_add.add_supplier'))

            # 4. تجهيز المورد
            new_supplier = Supplier(
                username=username, 
                trade_name=trade_name, 
                status='active'
            )
            new_supplier.phone = phone # استخدام الـ setter المشفر في الموديل
            new_supplier.set_password(password)
            
            # 5. الحفظ (يؤدي تلقائياً لتشغيل event after_insert وإنشاء المحفظة)
            db.session.add(new_supplier)
            db.session.commit()
            
            flash(f"تم إضافة الشريك {trade_name} بنجاح!", "success")
            return redirect(url_for('suppliers_add.add_supplier'))
            
        except Exception as e:
            db.session.rollback()
            # طباعة الخطأ في سجلات الخادم (Logs) لنعرف السبب الحقيقي
            logging.error(f"Error adding supplier: {str(e)}")
            flash(f"خطأ تقني: تعذر إضافة الشريك. يرجى مراجعة Logs الخادم.", "danger")
            return redirect(url_for('suppliers_add.add_supplier'))
        
    return render_template('suppliers_add/suppliers_add.html')
