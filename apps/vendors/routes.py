# coding: utf-8
# 📂 apps/vendors/routes.py - نظام إدارة الموردين والربط البرمجي

import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user # تأكد من استدعاء current_user إذا استخدمته
from apps.extensions import db
from apps.models import AdminUser, SupplierProfile
from werkzeug.utils import secure_filename
from datetime import datetime

# إعداد الـ Blueprint لنظام الموردين
vendors_bp = Blueprint('vendors', __name__, url_prefix='/vendors')

# إعداد مسار المجلد الخاص برفع صور المنتجات
UPLOAD_FOLDER = os.path.join('apps', 'static', 'uploads', 'products')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# ◄ تأمين وجود المجلد برمجياً لمنع انهيار رفع الصور على السيرفر
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- مسار تسجيل دخول الموردين ---
@vendors_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'supplier':
            return redirect(url_for('vendors.dashboard'))
        return redirect(url_for('main.index')) # أو المسار الافتراضي للمنصة
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = AdminUser.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.role != 'supplier':
                flash('عذراً، هذا الحساب ليس حساب مورد معتمد.', 'danger')
                return redirect(url_for('vendors.login'))
                
            if not user.is_active:
                flash('هذا الحساب معطل حالياً، يرجى مراجعة الإدارة السيادية.', 'danger')
                return redirect(url_for('vendors.login'))
                
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('vendors.dashboard'))
            
        flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
        
    return render_template('vendors/login.html')

# --- مسار تسجيل الخروج ---
@vendors_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج من نظام الموردين بنجاح.', 'success')
    return redirect(url_for('vendors.login'))
