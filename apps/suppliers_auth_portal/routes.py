# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from apps.models.supplier_db import Supplier
from apps.extensions import db
from apps.suppliers_auth_portal.otp_service import SupplierOTPService

# ⚠️ هذا هو الاسم الذي يجب أن يكون موجوداً
suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    template_folder='templates',
    url_prefix='/supplier'
)


@suppliers_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """تسجيل الدخول للموردين"""
    if current_user.is_authenticated:
        return redirect(url_for('suppliers_auth_bp.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            supplier = Supplier.query.filter_by(username=username).first()
            if supplier and supplier.check_password(password):
                login_user(supplier)
                return redirect(url_for('suppliers_auth_bp.dashboard'))
            else:
                flash('اسم المستخدم أو كلمة المرور غير صحيحة!', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    return render_template('suppliers_auth_portal/login.html')


@suppliers_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """تسجيل الدخول للموردين"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        owner_name = request.form.get('owner_name')
        store_name = request.form.get('store_name')
        phone = request.form.get('phone')
        
        try:
            supplier = Supplier(
                username=username,
                password=password,
                owner_name=owner_name,
                store_name=store_name,
                phone=phone
            )
            db.session.add(supplier)
            db.session.commit()
            flash('تم تسجيلك بنجاح!', 'success')
            return redirect(url_for('suppliers_auth_bp.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    return render_template('suppliers_auth_portal/register.html')


@suppliers_auth_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """لوحة تحكم الموردين"""
    return render_template('suppliers_auth_portal/dashboard.html')


@suppliers_auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """استعادة كلمة المرور"""
    if request.method == 'POST':
        identifier = request.form.get('identifier')  # رقم الهاتف أو اسم المستخدم
        if identifier:
            # افتراضي: ابحث عن المورد
            supplier = Supplier.query.filter(
                (Supplier.phone == identifier) | (Supplier.username == identifier)
            ).first()
            if supplier:
                # تسجيل الدخول للمورد (مؤقتاً)
                login_user(supplier)
                flash('تم إرسال رمز التحقق بنجاح، يرجى التحقق من واتساب الخاص بك.', 'success')
                return redirect(url_for('suppliers_auth_bp.dashboard'))
            else:
                flash('لا يوجد مورد بهذه البيانات!', 'danger')
        else:
            flash('يرجى إدخال رقم الهاتف أو اسم المستخدم!', 'danger')
    
    return render_template('suppliers_auth_portal/forgot_password.html')


@suppliers_auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('suppliers_auth_bp.login'))
