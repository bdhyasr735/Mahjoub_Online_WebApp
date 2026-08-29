# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/routes.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from sqlalchemy import or_

suppliers_auth_bp = Blueprint('suppliers_auth_bp', __name__, template_folder='templates')

@suppliers_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    تسجيل دخول المورد أو موظف المورد باستخدام:
    1. البريد الإلكتروني (Email)
    2. رقم الهاتف (Phone)
    3. اسم المستخدم (Username)
    """
    if current_user.is_authenticated:
        return redirect(url_for('suppliers_auth_bp.dashboard'))

    if request.method == 'POST':
        login_identifier = request.form.get('login_identifier', '').strip()
        password = request.form.get('password', '').strip()
        login_type = request.form.get('login_type', 'supplier') # supplier أو supplier_staff

        if not login_identifier or not password:
            flash("يرجى إدخال بيانات الدخول وكلمة المرور بشكل صحيح.", "danger")
            return render_template('suppliers/auth/login.html')

        try:
            user = None
            if login_type == 'supplier_staff':
                # البحث لموظف المورد عبر البريد أو اسم المستخدم أو الهاتف
                user = SupplierStaff.query.filter(
                    or_(
                        SupplierStaff.email == login_identifier,
                        SupplierStaff.username == login_identifier,
                        SupplierStaff.phone == login_identifier
                    )
                ).first()
                actual_user_type = 'supplier_staff'
            else:
                # البحث للمورد عبر البريد أو اسم المستخدم أو الهاتف
                user = Supplier.query.filter(
                    or_(
                        Supplier.email == login_identifier,
                        Supplier.username == login_identifier,
                        Supplier.phone == login_identifier,
                        Supplier.search_phone == login_identifier
                    )
                ).first()
                actual_user_type = 'supplier'

            if user and user.check_password(password):
                if getattr(user, 'status', 'active') != 'active':
                    flash("حسابك موقوف أو غير فعال، يرجى التواصل مع الإدارة.", "warning")
                    return render_template('suppliers/auth/login.html')

                login_user(user)
                session['user_type'] = actual_user_type
                flash("تم تسجيل الدخول بنجاح، أهلاً بك في لوحة تحكم الموردين.", "success")
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('suppliers_auth_bp.dashboard'))
            else:
                flash("بيانات الدخول غير صحيحة، تأكد من المعرف وكلمة المرور.", "danger")

        except Exception as e:
            db.session.rollback()
            flash(f"حدث خطأ أثناء تسجيل الدخول: {str(e)}", "danger")

    return render_template('suppliers/auth/login.html')

@suppliers_auth_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('suppliers/dashboard.html')

@suppliers_auth_bp.route('/logout')
@login_required
def logout():
    session.pop('user_type', None)
    logout_user()
    flash("تم تسجيل الخروج بنجاح.", "info")
    return redirect(url_for('suppliers_auth_bp.login'))
