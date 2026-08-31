# -*- coding: utf-8 -*-
# apps/auth_portal/routes.py

"""
مسارات وبوابات المصادقة السيادية الإدارية (Admin Auth Portal)
لمنصة محجوب أونلاين - متوافقة تماماً مع قالب واجهة تسجيل الدخول
"""

import logging
import re
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from apps.extensions import db
from apps.models.admin_db import Admin  # تأكد من تطابق مسار نموذج المشرفين في هيكلة مشروعك

# إعداد التسجيل (Logger)
logger = logging.getLogger(__name__)

# تعريف الـ Blueprint الخاص ببوابة الآدمن
auth_portal_bp = Blueprint(
    'auth_portal_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/admin-auth'  # يمكنك تعديل البادئة (Prefix) حسب رغبتك في توجيه الروابط
)


# ============================================================
# دوال مساعدة للتحقق من المدخلات
# ============================================================

def validate_username(username):
    """التحقق من صحة اسم المستخدم الإداري لمنع الحقن أو القيم الفارغة"""
    if not username:
        return None
    # السماح بالأحرف (الإنجليزية/العربية) والأرقام والشرطة السفلى
    cleaned = username.strip()
    if re.match(r'^[a-zA-Z0-9_\u0600-\u06FF]{3,50}$', cleaned):
        return cleaned
    return None


# ============================================================
# مسارات المصادقة والتحكم
# ============================================================

@auth_portal_bp.route('/login', methods=['GET'])
def login_page():
    """عرض صفحة تسجيل الدخول للبوابة السيادية الإدارية"""
    try:
        # إذا كان المشرف مسجلاً مسبقاً، يتم توجيهه مباشرة للوحة التحكم
        if current_user.is_authenticated and getattr(current_user, 'is_admin', True):
            return redirect(url_for('auth_portal_bp.dashboard'))
            
        return render_template(
            'auth/login.html', 
            page_title='البوابة السيادية الإدارية | محجوب أونلاين'
        )
    except Exception as e:
        logger.error(f"❌ خطأ فادح أثناء عرض صفحة دخول الآدمن: {str(e)}", exc_info=True)
        return f"Internal Server Error: {str(e)}", 500


@auth_portal_bp.route('/login', methods=['POST'])
def login():
    """معالجة طلب تسجيل الدخول القادم عبر الـ JSON من الواجهة الأمامية"""
    try:
        data = request.get_json(silent=True) or request.form
        if not data:
            return jsonify({'status': 'error', 'message': 'بيانات غير صالحة'}), 400

        username_input = str(data.get('username', '')).strip()
        password = str(data.get('password', ''))

        if not username_input or not password:
            return jsonify({'status': 'error', 'message': 'يرجى إدخال اسم المستخدم وكلمة المرور'}), 400

        valid_username = validate_username(username_input)
        if not valid_username:
            return jsonify({'status': 'error', 'message': 'صيغة اسم المستخدم الإداري غير صالحة'}), 400

        # البحث عن المشرف في قاعدة البيانات (سواء بالـ username أو الـ email)
        admin_user = Admin.query.filter(
            (Admin.username == valid_username) | (Admin.email == valid_username)
        ).first()

        if not admin_user:
            logger.warning(f"⚠️ محاولة تسجيل دخول فاشلة لمشرف غير موجود: {username_input}")
            return jsonify({'status': 'error', 'message': 'بيانات الدخول أو كلمة المرور غير صحيحة'}), 401

        # التحقق من كلمة المرور باستخدام الدوال المعتمدة
        password_valid = False
        if hasattr(admin_user, 'check_password'):
            password_valid = admin_user.check_password(password)
        elif hasattr(admin_user, 'password_hash'):
            from werkzeug.security import check_password_hash
            password_valid = check_password_hash(admin_user.password_hash, password)

        if not password_valid:
            logger.warning(f"⚠️ كلمة مرور خاطئة لمحاولة تسجيل دخول المشرف: {valid_username}")
            return jsonify({'status': 'error', 'message': 'بيانات الدخول أو كلمة المرور غير صحيحة'}), 401

        # التحقق من أن حساب المشرف نشط
        if hasattr(admin_user, 'is_active') and not admin_user.is_active:
            logger.warning(f"⚠️ محاولة دخول على حساب إداري معطل: {valid_username}")
            return jsonify({'status': 'error', 'message': 'هذا الحساب الإداري معطل. يرجى مراجعة الإدارة العليا.'}), 403

        # تسجيل الدخول بنجاح وتفعيل الجلسة عبر Flask-Login
        login_user(admin_user, remember=True)
        session['user_type'] = 'admin'
        session['login_time'] = datetime.now().isoformat()

        # تحديث وقت آخر تسجيل دخول إن وجد الحقل في قاعدة البيانات
        if hasattr(admin_user, 'last_login'):
            admin_user.last_login = datetime.now()
            db.session.commit()

        logger.info(f"🛡️ تم تسجيل دخول المشرف السيادي بنجاح: {admin_user.username}")
        
        # الرد بالصيغة المتوافقة تماماً مع الـ JavaScript في القالب الأمامي
        return jsonify({
            'status': 'success',
            'message': 'تم التحقق بنجاح. جاري توجيهك إلى النظام السيادي...',
            'redirect': url_for('auth_portal_bp.dashboard')
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ غير متوقع أثناء معالجة تسجيل دخول الآدمن: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'خطأ داخلي في الخادم: {str(e)}'}), 500


@auth_portal_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم السيادية الإدارية الرئيسية"""
    try:
        # التحقق الإضافي من الصلاحيات ونوع الجلسة للأمان العالي
        if session.get('user_type') != 'admin' and not getattr(current_user, 'is_admin', True):
            logout_user()
            return redirect(url_for('auth_portal_bp.login_page'))

        return render_template(
            'auth/dashboard.html',
            page_title='لوحة التحكم السيادية | محجوب أونلاين',
            admin_user=current_user
        )
    except Exception as e:
        logger.error(f"❌ خطأ في عرض لوحة التحكم السيادية: {str(e)}", exc_info=True)
        return f"Internal Server Error: {str(e)}", 500


@auth_portal_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """تسجيل الخروج وإنهاء الجلسة السيادية للأدمن"""
    try:
        admin_name = getattr(current_user, 'username', 'Unknown')
        logout_user()
        session.clear()
        logger.info(f"🔒 تم تسجيل خروج المشرف السيادي: {admin_name}")
    except Exception as e:
        logger.error(f"❌ خطأ أثناء تسجيل الخروج: {str(e)}", exc_info=True)
        
    return redirect(url_for('auth_portal_bp.login_page'))


# ============================================================
# دالة تهيئة التطبيق (App Initialization)
# ============================================================

def init_app(app):
    """تسجيل الـ Blueprint ضمن تطبيق Flask الرئيسي"""
    if not app.blueprints.get('auth_portal_bp'):
        app.register_blueprint(auth_portal_bp)
    
    logger.info("✅ تم تسجيل وتهيئة مسارات البوابة السيادية الإدارية بنجاح.")
    return app
