# -*- coding: utf-8 -*-
# 📂 apps/auth_portal/routes.py

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
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
            return redirect(request.args.get('next') or '/dashboard')
        return redirect('/dashboard')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('الرجاء إدخال اسم المستخدم وكلمة المرور', 'danger')
            return render_template('auth/login.html')

        try:
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
                    flash('هذا الحساب معطل، يرجى مراجعة الإدارة', 'danger')
                    return render_template('auth/login.html')

                # تسجيل الدخول عبر Flask-Login
                login_user(user, remember=True)
                session['user_type'] = user_type
                session.permanent = True
                
                next_page = request.form.get('next') or request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('/dashboard')

            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')

        except Exception as e:
            db.session.rollback()
            print(f"❌ [خطأ في تسجيل الدخول]: {e}")
            flash('حدث خطأ في النظام، يرجى المحاولة لاحقاً', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """تسجيل الخروج وإنهاء الجلسة بأمان"""
    session.pop('user_type', None)
    logout_user()
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    
    # التحقق من معامل next الممرر أو العودة لمسار تسجيل الدخول الافتراضي
    next_url = request.args.get('next') or request.form.get('next')
    if next_url:
        return redirect(next_url)

    admin_login_path = os.environ.get('ADMIN_LOGIN_PATH', '/auth/m7jb_sovereign_hq_v2_99x')
    return redirect(admin_login_path)
