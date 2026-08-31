# -*- coding: utf-8 -*-
# 📂 apps/auth_portal/routes.py

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from apps.extensions import db
from apps.models.admin_db import AdminUser
from apps.models.admin_staff_db import AdminStaff

auth_bp = Blueprint('auth_portal', __name__, template_folder='templates', static_folder='static')

@auth_bp.route('/m7jb_sovereign_hq_v2_99x', methods=['GET', 'POST'])
def sovereign_login():
    """مسار تسجيل الدخول السيادي الإداري المخصص"""
    # إذا كان المستخدم مسجلاً دخوله مسبقاً، يتم توجيهه إلى لوحة التحكم مباشرة
    if current_user.is_authenticated:
        if isinstance(current_user, (AdminUser, AdminStaff)):
            return redirect(url_for('admin_dashboard.index') if 'admin_dashboard.index' in [p.endpoint for p in auth_bp.app.view_functions.values() or []] else '/dashboard')
        return redirect('/dashboard')

    if request.method == 'POST':
        # دعم استقبال البيانات كـ JSON أو Form Data لتفادي أخطاء 400
        data = request.get_json(silent=True) or request.form
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            if request.is_json:
                return jsonify({"success": False, "message": "الرجاء إدخال اسم المستخدم وكلمة المرور"}), 400
            flash('الرجاء إدخال اسم المستخدم وكلمة المرور', 'danger')
            return render_template('auth/login.html')

        # 1. البحث في جدول مسؤولي النظام (AdminUser)
        user = AdminUser.query.filter_by(username=username).first()
        user_type = 'admin'

        # 2. إذا لم يوجد، البحث في جدول موظفي الإدارة (AdminStaff)
        if not user:
            user = AdminStaff.query.filter_by(username=username).first()
            user_type = 'admin_staff'

        if user and user.check_password(password):
            # التحقق مما إذا كان حساب الموظف مفَعلاً (إن وجد الحقل)
            if user_type == 'admin_staff' and hasattr(user, 'is_active') and not user.is_active:
                if request.is_json:
                    return jsonify({"success": False, "message": "هذا الحساب معطل، يرجى مراجعة الإدارة"}), 403
                flash('هذا الحساب معطل، يرجى مراجعة الإدارة', 'danger')
                return render_template('auth/login.html')

            # تسجيل الدخول عبر Flask-Login
            login_user(user, remember=True)
            session['user_type'] = user_type
            session.permanent = True

            if request.is_json:
                return jsonify({"success": True, "redirect_url": "/dashboard"})
            
            return redirect('/dashboard')

        if request.is_json:
            return jsonify({"success": False, "message": "اسم المستخدم أو كلمة المرور غير صحيحة"}), 401
        
        flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """تسجيل الخروج وإنهاء الجلسة بأمان"""
    session.pop('user_type', None)
    logout_user()
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    
    admin_login_path = os.environ.get('ADMIN_LOGIN_PATH', '/auth/m7jb_sovereign_hq_v2_99x')
    return redirect(admin_login_path)
