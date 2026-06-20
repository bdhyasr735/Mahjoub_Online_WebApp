# coding: utf-8
# 📂 apps/vendors/routes.py - نظام إدارة الموردين والربط البرمجي الموحد

import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from apps.extensions import db
from apps.models import AdminUser, SupplierProfile  # استدعاء علوي استراتيجي لفك جمود علاقات قاعدة البيانات فوراً
from werkzeug.utils import secure_filename
from datetime import datetime

# إعداد الـ Blueprint لنظام الموردين بنطاق معزول
vendors_bp = Blueprint('vendors', __name__, url_prefix='/vendors')

# إعداد وتأمين مسار المجلد الخاص برفع صور المنتجات
UPLOAD_FOLDER = os.path.join('apps', 'static', 'uploads', 'products')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# حوكمة المجلد: إنشاء المسار تلقائياً إن لم يكن موجوداً لمنع خطأ FileNotFoundError
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """التحقق من سلامة وامتداد ملفات الصور المرفوعة"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- مسار تسجيل دخول الموردين ---
@vendors_bp.route('/login', methods=['GET', 'POST'])
def login():
    # منع المورد المسجل دخولاً بالفعل من إعادة رؤية صفحة الدخول
    if current_user.is_authenticated:
        if current_user.role == 'supplier':
            return redirect(url_for('vendors.dashboard'))
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # استعلام سيادي لفحص الحساب عبر اسم المستخدم
        user = AdminUser.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # فحص الصلاحيات والأدوار للتأكد من هوية المورد
            if user.role != 'supplier':
                flash('عذراً، هذا الحساب ليس حساب مورد معتمد.', 'danger')
                return redirect(url_for('vendors.login'))
                
            # فحص حالة الحساب التشغيلية
            if not user.is_active:
                flash('هذا الحساب معطل حالياً، يرجى مراجعة الإدارة السيادية.', 'danger')
                return redirect(url_for('vendors.login'))
                
            # إتمام عملية الولوج وتحديث طابع وقت آخر ظهور
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('vendors.dashboard'))
            
        flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
        
    return render_template('vendors/login.html')

# --- مسار لوحة تحكم المورد المعزولة ---
@vendors_bp.route('/dashboard')
@login_required
def dashboard():
    # تأمين الواجهة التأكيدي: منع أي رتبة أخرى من استعراض بيانات المورد
    if current_user.role != 'supplier':
        flash('غير مصرح لك بدخول هذه اللوحة.', 'danger')
        return redirect(url_for('auth_portal.login'))
    return render_template('vendors/dashboard.html')

# --- مسار تسجيل الخروج ---
@vendors_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج من نظام الموردين بنجاح.', 'success')
    return redirect(url_for('vendors.login'))
