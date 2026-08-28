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

        user, user_type = authenticate_supplier(login_input, password)

        if user:
            login_user(user, remember=remember)
            session['user_type'] = user_type
            
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
    if not isinstance(current_user, (Supplier, SupplierStaff)):
        flash('غير مصرح لك بالوصول إلى لوحة تحكم الموردين.', 'danger')
        return redirect(url_for('suppliers_bp.login'))

    supplier_obj = current_user if isinstance(current_user, Supplier) else db.session.get(Supplier, current_user.supplier_id)
    return render_template('suppliers_auth_portal/dashboard.html', supplier=supplier_obj)


@suppliers_bp.route('/logout')
@login_required
def logout():
    session.pop('user_type', None)
    session.pop('supplier_id', None)
    session.pop('supplier_staff_id', None)
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('suppliers_bp.login'))
