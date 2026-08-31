# -*- coding: utf-8 -*-
# apps/auth_portal/routes.py

"""
مسارات وبوابات المصادقة السيادية الإدارية (Admin Auth Portal)
متوافقة صراحةً مع جداول قاعدة البيانات والكيانات الفعلية لنظام محجوب أونلاين
"""

import logging
import re
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from apps.extensions import db
from apps.models.admin_db import AdminUser  # الجدول والحقل الصريح المعتمد في الهيكل

logger = logging.getLogger(__name__)

# تعريف الـ Blueprint بالمسار السيادي الأصلي
auth_portal_bp = Blueprint(
    'auth_portal_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/m7jb_sovereign_hq_v2_99x'
)


def validate_username(username):
    """التحقق الصريح من مطابقة صيغة اسم المستخدم أو البريد الإداري"""
    if not username:
        return None
    cleaned = username.strip()
    if re.match(r'^[a-zA-Z0-9_@.\-\u0600-\u06FF]{3,100}$', cleaned):
        return cleaned
    return None


@auth_portal_bp.route('/login', methods=['GET'])
def login_page():
    """عرض صفحة تسجيل الدخول السيادية"""
    try:
        if current_user.is_authenticated and isinstance(current_user, AdminUser):
            return redirect(url_for('auth_portal_bp.dashboard'))
            
        return render_template(
            'auth/login.html', 
            page_title='البوابة السيادية الإدارية | محجوب أونلاين'
        )
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل واجهة الدخول السيادية: {str(e)}", exc_info=True)
        return f"Internal Server Error: {str(e)}", 500


@auth_portal_bp.route('/login', methods=['POST'])
def login():
    """معالجة عملية التحقق والمطابقة الصريحة مع أعمدة جدول المشرفين في قاعدة البيانات"""
    try:
        data = request.get_json(silent=True) or request.form
        if not data:
            return jsonify({'status': 'error', 'message': 'بيانات الإدخال غير صالحة'}), 400

        username_input = str(data.get('username', '')).strip()
        password = str(data.get('password', ''))

        if not username_input or not password:
            return jsonify({'status': 'error', 'message': 'يرجى إدخال اسم المستخدم وكلمة المرور بدقة'}), 400

        valid_input = validate_username(username_input)
        if not valid_input:
            return jsonify({'status': 'error', 'message': 'صيغة البيانات المدخلة لا تتطابق مع المعايير'}), 400

        # الاستعلام الصريح من جدول AdminUser بالاعتماد على الأعمدة الفعلية (username أو email)
        admin_user = AdminUser.query.filter(
            (AdminUser.username == valid_input) | (AdminUser.email == valid_input)
        ).first()

        if not admin_user:
            logger.warning(f"⚠️ محاولة دخول مرفوضة لحساب غير موجود: {username_input}")
            return jsonify({'status': 'error', 'message': 'اسم المستخدم أو كلمة المرور غير مطابقة للبيانات المخزنة'}), 401

        # التحقق المطابق من حقل كلمة المرور المشفرة (password_hash)
        password_valid = False
        if hasattr(admin_user, 'check_password'):
            password_valid = admin_user.check_password(password)
        elif hasattr(admin_user, 'password_hash'):
            from werkzeug.security import check_password_hash
            password_valid = check_password_hash(admin_user.password_hash, password)

        if not password_valid:
            logger.warning(f"⚠️ خطأ في مطابقة كلمة المرور للمشرف: {valid_input}")
            return jsonify({'status': 'error', 'message': 'اسم المستخدم أو كلمة المرور غير مطابقة للبيانات المخزنة'}), 401

        # التحقق الصريح من حالة نشاط الحساب إذا وجد الحقل في الجدول
        if hasattr(admin_user, 'is_active') and not admin_user.is_active:
            logger.warning(f"⚠️ محاولة وصول لحساب إداري موقوف: {valid_input}")
            return jsonify({'status': 'error', 'message': 'هذا الحساب الإداري غير موصول أو تم إيقافه.'}), 403

        # اعتماد جلسة الدخول البرمجية للمشرف
        login_user(admin_user, remember=True)
        session['user_type'] = 'admin'
        session['login_time'] = datetime.now().isoformat()

        # تحديث حقل وقت آخر تسجيل دخول صراحةً إن وجد في الجدول
        if hasattr(admin_user, 'last_login'):
            admin_user.last_login = datetime.now()
            db.session.commit()

        logger.info(f"🛡️ تمت مطابقة البيانات بنجاح ودخول المشرف السيادي: {admin_user.username}")
        
        return jsonify({
            'status': 'success',
            'message': 'تم مطابقة البيانات بنجاح. جاري فتح لوحة التحكم السيادية...',
            'redirect': url_for('auth_portal_bp.dashboard')
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ استثنائي أثناء معالجة مطابقة بيانات الآدمن: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'خطأ داخلي في مطابقة البيانات: {str(e)}'}), 500


@auth_portal_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم السيادية الإدارية"""
    try:
        if session.get('user_type') != 'admin' or not isinstance(current_user, AdminUser):
            logout_user()
            return redirect(url_for('auth_portal_bp.login_page'))

        return render_template(
            'auth/dashboard.html',
            page_title='لوحة التحكم السيادية | محجوب أونلاين',
            admin_user=current_user
        )
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل لوحة التحكم السيادية: {str(e)}", exc_info=True)
        return f"Internal Server Error: {str(e)}", 500


@auth_portal_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """إنهاء الجلسة السيادية وتسجيل الخروج"""
    try:
        admin_name = getattr(current_user, 'username', 'Unknown')
        logout_user()
        session.clear()
        logger.info(f"🔒 تم إنهاء الجلسة السيادية للمشرف: {admin_name}")
    except Exception as e:
        logger.error(f"❌ خطأ أثناء تسجيل الخروج: {str(e)}", exc_info=True)
        
    return redirect(url_for('auth_portal_bp.login_page'))


def init_app(app):
    """تهيئة وتسجيل المسارات صراحةً في تطبيق الفلاسك"""
    if not app.blueprints.get('auth_portal_bp'):
        app.register_blueprint(auth_portal_bp)
    
    from apps.extensions import csrf
    try:
        csrf.exempt(auth_portal_bp)
    except Exception:
        pass

    logger.info("✅ تم إتمام مطابقة وتهيئة مسارات بوابة الأدمن الصريحة بنجاح.")
    return app
