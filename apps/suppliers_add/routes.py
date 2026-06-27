# 📂 apps/suppliers_add/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required # أضفنا حماية لتسجيل الدخول
from apps.models.supplier_db import Supplier
from apps.extensions import db

# تأكد أن template_folder يشير إلى المجلد الصحيح بالنسبة لملف routes.py
suppliers_add_bp = Blueprint(
    'suppliers_add', 
    __name__, 
    template_folder='templates'
)

@suppliers_add_bp.route('/add', methods=['GET', 'POST'])
@login_required # حماية: لا يمكن إضافة مورد إلا إذا كان المسؤول مسجلاً دخوله
def add_supplier():
    if request.method == 'POST':
        try:
            # استقبال البيانات
            username = request.form.get('username')
            trade_name = request.form.get('trade_name')
            phone = request.form.get('phone')
            password = request.form.get('password')

            # التحقق من البيانات المطلوبة
            if not username or not password:
                flash("يرجى تعبئة كافة الحقول المطلوبة", "danger")
                return redirect(url_for('suppliers_add.add_supplier'))

            # التحقق من وجود المستخدم مسبقاً
            if Supplier.query.filter_by(username=username).first():
                flash("اسم المستخدم موجود مسبقاً!", "danger")
                return redirect(url_for('suppliers_add.add_supplier'))

            # إنشاء كائن المورد
            new_supplier = Supplier(
                username=username, 
                trade_name=trade_name, 
                phone=phone, 
                status='active'
            )
            new_supplier.set_password(password)
            
            db.session.add(new_supplier)
            db.session.commit() # هنا يتم تشغيل الـ after_insert وإنشاء المحفظة
            
            flash(f"تم إضافة المورد {trade_name} بنجاح!", "success")
            return redirect(url_for('suppliers_add.add_supplier'))
            
        except Exception as e:
            db.session.rollback() # تراجع عن العملية في حال حدوث خطأ
            flash(f"حدث خطأ أثناء الحفظ: {str(e)}", "danger")
            return redirect(url_for('suppliers_add.add_supplier'))
        
    return render_template('suppliers_add/suppliers_add.html')
