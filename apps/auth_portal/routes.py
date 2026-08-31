# -*- coding: utf-8 -*-
# apps/admin_auth_portal/routes.py

"""
مسارات المصادقة والتحكم الخاصة بمديري النظام (Admin Portal)
يعتمد على النماذج الموحدة والآمنة في منصة محجوب أونلاين
"""

import logging
import re
import os
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from apps.extensions import db
from apps.models.admin_db import Admin  # افترض أن نموذج الآدمن موجود بهذا المسار أو يتم تعديله حسب هيكلتك

# إعداد التسجيل
logger = logging.getLogger(__name__)

# إنشاء Blueprint الخاص بالآدمن
admin_auth_bp = Blueprint(
    'admin_auth_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/admin-portal'
)


# ============================================================
# دوال مساعدة للتحقق
# ============================================================

def validate_email(email):
    """التحقق من صحة البريد الإلكتروني للآدمن"""
    if not email:
        return None
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_regex, email):
        return email.lower()
    return None


# ============================================================
# مسارات المصادقة الخاصة بالآدمن
# ============================================================

@admin_auth_bp.route('/login', methods=['GET'])
def admin_login_page():
    """عرض صفحة تسجيل دخول الآدمن"""
    try:
        if current_user.is_authenticated and getattr(current_user, 'is_admin', False):
            return redirect(url_for('admin_auth_bp.admin_dashboard'))
        return render_template('admin_auth_portal/login.html', page_title='تسجيل دخول المشرفين | محجوب أونلاين')
    except Exception as e:
        logger.error(f"❌ خطأ أثناء عرض صفحة دخول الآدمن: {str(e)}", exc_info=True)
        return f"Internal Server Error: {str(e)}", 500


@admin_auth_bp.route('/login', methods=['POST'])
def admin_login():
    """معالجة تسجيل دخول الآدمن (JSON / Form)"""
    try:
        data = request.get_json(silent=True) or request.form
        if not data:
            return jsonify({'success': False, 'message': 'بيانات غير صالحة'}), 400

        identifier = str(data.get('identifier', '')).strip()
        password = str(data.get('password', ''))
        remember_me = bool(data.get('remember_me', False))

        if not identifier or not password:
            return jsonify({'success': False, 'message': 'يرجى إدخال البريد الإلكتروني أو اسم المستخدم وكلمة المرور'}), 400

        # البحث عن المشرف (سواء بالبريد أو اسم المستخدم)
        admin_user = None
        email = validate_email(identifier)
        if email:
            admin_user = Admin.query.filter_by(email=email).first()
        
        if not admin_user:
            admin_user = Admin.query.filter(
                (Admin.username == identifier) | (Admin.email == identifier)
            ).first()

        if not admin_user:
            logger.warning(f"⚠️ محاولة تسجيل دخول فاشلة لمشرف غير موجود: {identifier}")
            return jsonify({'success': False, 'message': 'بيانات الدخول غير صحيحة'}), 401

        # التحقق من كلمة المرور
        password_valid = False
        if hasattr(admin_user, 'check_password'):
            password_valid = admin_user.check_password(password)
        elif hasattr(admin_user, 'password_hash'):
            from werkzeug.security import check_password_hash
            password_valid = check_password_hash(admin_user.password_hash, password)

        if not password_valid:
            logger.warning(f"⚠️ كلمة مرور خاطئة لمحاولة تسجيل دخول الآدمن: {identifier}")
            return jsonify({'success': False, 'message': 'بيانات الدخول غير صحيحة'}), 401

        # التأكد من أن الحساب نشط ولديه صلاحيات مشرف
        if hasattr(admin_user, 'is_active') and not admin_user.is_active:
            return jsonify({'success': False, 'message': 'حساب المشرف هذا معطل. يراجع مسؤول النظام.'}), 403

        # إتمام عملية تسجيل الدخول عبر Flask-Login
        login_user(admin_user, remember=remember_me)
        session['user_type'] = 'admin'
        session['login_time'] = datetime.now().isoformat()

        if hasattr(admin_user, 'last_login'):
            admin_user.last_login = datetime.now()
            db.session.commit()

        logger.info(f"🛡️ تم تسجيل دخول المشرف بنجاح: {admin_user.username}")
        return jsonify({
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'redirect_url': url_for('admin_auth_bp.admin_dashboard')
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ غير متوقع أثناء تسجيل دخول الآدمن: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'خطأ داخلي في الخادم: {str(e)}'}), 500


@admin_auth_bp.route('/dashboard')
@login_required
def admin_dashboard():
    """لوحة التحكم الرئيسية للآدمن"""
    try:
        # التأكد من أن المستخدم الحالي هو آدمن فعلياً
        if session.get('user_type') != 'admin' and not getattr(current_user, 'is_admin', False):
            logout_user()
            return redirect(url_for('admin_auth_bp.admin_login_page'))

        return render_template(
            'admin/dashboard.html',
            page_title='لوحة التحكم الإدارية | محجوب أونلاين',
            admin_user=current_user
        )
    except Exception as e:
        logger.error(f"❌ خطأ في عرض لوحة تحكم الآدمن: {str(e)}", exc_info=True)
        return f"Internal Server Error: {str(e)}", 500


@admin_auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def admin_logout():
    """تسجيل خروج الآدمن"""
    logout_user()
    session.clear()
    return redirect(url_for('admin_auth_bp.admin_login_page'))


# ============================================================
# التهيئة العامة
# ============================================================

def init_admin_app(app):
    """تهيئة تطبيق الآدمن وتسجيل الـ Blueprint"""
    if not app.blueprints.get('admin_auth_bp'):
        app.register_blueprint(admin_auth_bp)
    
    logger.info("✅ تم تهيئة بوابة المشرفين (Admin Portal) بنجاح مع معايير الأمان المتقدمة.")
    return app
