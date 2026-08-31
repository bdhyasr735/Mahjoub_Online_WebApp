# -*- coding: utf-8 -*-
# apps/auth_portal/routes.py

"""
مسارات وبوابات المصادقة السيادية الإدارية (Admin Staff Auth Portal)
متوافقة صراحةً مع جدول وموديل AdminStaff في قاعدة البيانات مع معالجة مرنة للطلبات وأخطاء الخادم
"""

import logging
import re
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from apps.extensions import db
from apps.models.admin_staff_db import AdminStaff

logger = logging.getLogger(__name__)

auth_portal_bp = Blueprint(
    'auth_portal_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/m7jb_sovereign_hq_v2_99x'
)


def validate_input(val):
    """التحقق الصريح من صيغة المدخلات (اسم مستخدم أو بريد إلكتروني)"""
    if not val:
        return None
    cleaned = val.strip()
    if re.match(r'^[a-zA-Z0-9_@.\-\u0600-\u06FF]{3,120}$', cleaned):
        return cleaned
    return None


@auth_portal_bp.route('/login', methods=['GET'])
def login_page():
    """عرض واجهة تسجيل الدخول السيادية"""
    try:
        if current_user.is_authenticated and isinstance(current_user, AdminStaff):
            return redirect(url_for('auth_portal_bp.dashboard'))
            
        return render_template(
            'auth/login.html', 
            page_title='البوابة السيادية الإدارية | محجوب أونلاين'
        )
    except Exception as e:
        logger.error(f"❌ خطأ في عرض صفحة الدخول: {str(e)}", exc_info=True)
        return f"Internal Server Error: {str(e)}", 500


@auth_portal_bp.route('/login', methods=['POST'])
def login():
    """معالجة الدخول مع التعامل المرن جداً مع كافة صيغ الطلبات (JSON, Form, Multi-part)"""
    try:
        data = {}
        
        # محاولة قراءة البيانات بكل الطرق المتاحة لضمان عدم فشل الاستلام
        if request.is_json:
            data = request.get_json(silent=True) or {}
        elif request.form:
            data = request.form.to_dict()
        else:
            try:
                data = request.get_json(force=True, silent=True) or {}
            except Exception:
                if request.data:
                    import json
                    try:
                        data = json.loads(request.data.decode('utf-8'))
                    except Exception:
                        data = {}

        # إذا كانت البيانات فارغة نهائياً، نجرب قراءة الـ form مباشرة حتى لو لم يتم تفعيل ترويسة الفورم
        if not data and request.form:
            data = request.form.to_dict()

        login_input = str(data.get('username', '')).strip()
        password = str(data.get('password', ''))

        if not login_input or not password:
            return jsonify({'status': 'error', 'message': 'يرجى إدخال اسم المستخدم/البريد وكلمة المرور'}), 400

        valid_input = validate_input(login_input)
        if not valid_input:
            return jsonify({'status': 'error', 'message': 'صيغة البيانات المدخلة غير مطابقة للمعايير'}), 400

        admin_staff = AdminStaff.query.filter(
            (AdminStaff.username == valid_input) | (AdminStaff.email == valid_input)
        ).first()

        if not admin_staff or not admin_staff.check_password(password):
            logger.warning(f"⚠️ محاولة دخول فاشلة (اسم مستخدم غير موجود أو كلمة مرور خاطئة): {login_input}")
            return jsonify({'status': 'error', 'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'}), 401

        if hasattr(admin_staff, 'is_active') and not admin_staff.is_active:
            logger.warning(f"⚠️ محاولة دخول على حساب إداري معطل: {valid_input}")
            return jsonify({'status': 'error', 'message': 'هذا الحساب الإداري معطل. يرجى مراجعة الإدارة العليا.'}), 403

        login_user(admin_staff, remember=True)
        session['user_type'] = 'admin_staff'
        session['login_time'] = datetime.now().isoformat()

        logger.info(f"🛡️ تم تسجيل دخول المشرف/الموظف بنجاح: {admin_staff.username}")
        
        return jsonify({
            'status': 'success',
            'message': 'تم التحقق بنجاح. جاري التوجيه إلى النظام السيادي...',
            'redirect': url_for('auth_portal_bp.dashboard')
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ فادح أثناء معالجة تسجيل الدخول: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'خطأ داخلي في الخادم: {str(e)}'}), 500


@auth_portal_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم السيادية الإدارية"""
    try:
        if session.get('user_type') != 'admin_staff' or not isinstance(current_user, AdminStaff):
            logout_user()
            return redirect(url_for('auth_portal_bp.login_page'))

        return render_template(
            'auth/dashboard.html',
            page_title='لوحة التحكم السيادية | محجوب أونلاين',
            admin_user=current_user
        )
    except Exception as e:
        logger.error(f"❌ خطأ في عرض لوحة التحكم: {str(e)}", exc_info=True)
        return f"Internal Server Error: {str(e)}", 500


@auth_portal_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """إنهاء الجلسة وتسجيل الخروج"""
    try:
        staff_name = getattr(current_user, 'username', 'Unknown')
        logout_user()
        session.clear()
        logger.info(f"🔒 تسجيل خروج الموظف/المشرف: {staff_name}")
    except Exception as e:
        logger.error(f"❌ خطأ أثناء تسجيل الخروج: {str(e)}", exc_info=True)
        
    return redirect(url_for('auth_portal_bp.login_page'))


def init_app(app):
    """تسجيل المسارات صراحةً"""
    if not app.blueprints.get('auth_portal_bp'):
        app.register_blueprint(auth_portal_bp)
    
    from apps.extensions import csrf
    try:
        csrf.exempt(auth_portal_bp)
    except Exception:
        pass

    logger.info("✅ تم ربط وتهيئة مسارات بوابة الموظفين الإداريين بالموديل الصريح بنجاح.")
    return app
