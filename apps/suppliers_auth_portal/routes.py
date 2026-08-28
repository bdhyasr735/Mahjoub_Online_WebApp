# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/routes.py

from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from apps.suppliers_auth_portal import suppliers_bp
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.extensions import db
from apps.suppliers_auth_portal.auth_service import authenticate_supplier

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    """معالجة تسجيل دخول الموردين أو موظفي الموردين."""
    if current_user.is_authenticated:
        if isinstance(current_user, (Supplier, SupplierStaff)):
            return redirect(url_for('suppliers_bp.dashboard'))

    if request.method == 'POST':
        login_input = request.form.get('username') or request.form.get('identifier') or request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        if not login_input or not password:
            flash('يرجى إدخال اسم المستخدم/رقم الهاتف وكلمة المرور.', 'danger')
            return render_template('suppliers_auth_portal/login.html')

        # استخدام خدمة المصادقة المركزية للبحث والتحقق (يدعم اسم المستخدم، البريد، أو الهاتف)
        user, user_type = authenticate_supplier(login_input, password)

        if user:
            # تسجيل الدخول عبر Flask-Login وتحديد نوع المستخدم في الجلسة
            login_user(user, remember=remember)
            session['user_type'] = user_type
            
            # ضبط المعرفات الخاصة بالمورد في الجلسة لتسهيل عمل لوحة التحكم
            if user_type == 'supplier':
                session['supplier_id'] = user.id
            elif user_type == 'supplier_staff':
                session['supplier_id'] = user.supplier_id
                session['supplier_staff_id'] = user.id

            flash('تم تسجيل الدخول بنجاح.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('suppliers_bp.dashboard'))
        else:
            flash('خطأ في بيانات الاعتماد: اسم المستخدم أو كلمة المرور غير صحيح.', 'danger')

    return render_template('suppliers_auth_portal/login.html')


@suppliers_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة تحكم المورد الرئيسية."""
    if not isinstance(current_user, (Supplier, SupplierStaff)):
        flash('غير مصرح لك بالوصول إلى لوحة تحكم الموردين.', 'danger')
        return redirect(url_for('suppliers_bp.login'))

    supplier_obj = current_user if isinstance(current_user, Supplier) else db.session.get(Supplier, current_user.supplier_id)
    
    return render_template('suppliers_auth_portal/dashboard.html', supplier=supplier_obj)


@suppliers_bp.route('/logout')
@login_required
def logout():
    """تسجيل خروج المورد وتفريغ الجلسة."""
    session.pop('user_type', None)
    session.pop('supplier_id', None)
    session.pop('supplier_staff_id', None)
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('suppliers_bp.login'))


@suppliers_bp.route('/register', methods=['GET', 'POST'])
def register():
    """تسجيل حساب مورد جديد."""
    if request.method == 'POST':
        trade_name = request.form.get('trade_name')
        owner_name = request.form.get('owner_name')
        phone = request.form.get('phone')
        password = request.form.get('password')

        if not trade_name or not phone or not password:
            flash('يرجى تعبئة الحقول الإجبارية.', 'danger')
            return render_template('suppliers_auth_portal/register.html')

        existing_supplier = Supplier.query.filter_by(phone=phone).first()
        if existing_supplier:
            flash('رقم الهاتف مسجل مسبقاً، يرجى تسجيل الدخول.', 'warning')
            return redirect(url_for('suppliers_bp.login'))

        new_supplier = Supplier(
            trade_name=trade_name,
            owner_name=owner_name,
            phone=phone,
            status='active'
        )
        new_supplier.set_password(password)

        try:
            db.session.add(new_supplier)
            db.session.commit()
            flash('تم إنشاء الحساب بنجاح، يمكنك تسجيل الدخول الآن.', 'success')
            return redirect(url_for('suppliers_bp.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء التسجيل: {str(e)}', 'danger')

    return render_template('suppliers_auth_portal/register.html')


@suppliers_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """استعادة كلمة المرور للموردين."""
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        supplier = Supplier.query.filter((Supplier.phone == identifier) | (Supplier.username == identifier) | (Supplier.email == identifier)).first()
        
        if supplier:
            flash('تم إرسال تعليمات استعادة كلمة المرور إلى الوسيلة المسجلة.', 'info')
        else:
            flash('لم يتم العثور على حساب بهذا المعرف.', 'danger')
            
    return render_template('suppliers_auth_portal/forgot_password.html')
