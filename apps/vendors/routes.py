# coding: utf-8
# 📂 apps/vendors/routes.py - نظام إدارة الموردين والربط البرمجي الموحد

import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from apps.extensions import db
from apps.models import AdminUser, SupplierProfile
from datetime import datetime

# إعداد الـ Blueprint مع نطاق مسار الموردين الجديد
vendors_bp = Blueprint('vendors', __name__, url_prefix='/supplier')

# --- دالة زراعة المستخدمين (للإدارة فقط) ---
def seed_user(username, password, role, is_active=True):
    existing = AdminUser.query.filter_by(username=username).first()
    if existing:
        return f"المستخدم {username} موجود مسبقاً."
    
    new_user = AdminUser(username=username, role=role, is_active=is_active)
    new_user.set_password(password) # تأكد أن هذه الدالة معرفة في موديل AdminUser
    db.session.add(new_user)
    db.session.commit()
    return f"تم إنشاء {role} بنجاح: {username}"

@vendors_bp.route('/seed-data')
@login_required
def seed_data():
    if current_user.role != 'admin':
        return "غير مصرح لك بالوصول", 403
    msg1 = seed_user('supplier_01', '123456', 'supplier')
    msg2 = seed_user('staff_01', '123456', 'staff')
    return f"{msg1} <br> {msg2}"

# --- مسار تسجيل دخول الموردين ---
@vendors_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'supplier':
            return redirect(url_for('vendors.dashboard'))
        return redirect(url_for('main.index')) # تأكد من وجود مسار index
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = AdminUser.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.role != 'supplier':
                flash('عذراً، هذا الحساب ليس حساب مورد معتمد.', 'danger')
                return redirect(url_for('vendors.login'))
                
            if not user.is_active:
                flash('هذا الحساب معطل حالياً.', 'danger')
                return redirect(url_for('vendors.login'))
                
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('vendors.dashboard'))
            
        flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
        
    return render_template('vendor/login.html') # تأكد من اسم المجلد (vendor)

# --- مسار لوحة تحكم المورد ---
@vendors_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'supplier':
        flash('غير مصرح لك بدخول هذه اللوحة.', 'danger')
        return redirect(url_for('vendors.login'))
    return render_template('vendor/dashboard.html')

# --- مسار تسجيل الخروج ---
@vendors_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('vendors.login'))
