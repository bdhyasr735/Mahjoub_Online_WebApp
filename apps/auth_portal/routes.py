# -*- coding: utf-8 -*-
# 📂 apps/auth_portal/routes.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, abort
from apps.models.admin_db import AdminUser
from apps.models.admin_staff_db import AdminStaff
import traceback

auth_portal = Blueprint('auth_portal', __name__, template_folder='templates')
auth_portal_bp = auth_portal

SECRET_ADMIN_PATH = '/auth/m7jb_sovereign_hq_v2_99x' # تم توحيد المسار ليطابق إعدادات التطبيق

@auth_portal.route(SECRET_ADMIN_PATH, methods=['GET', 'POST'])
def secure_admin_login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    try:
        data = request.get_json(silent=True) or request.form
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                "status": "error",
                "message": "يرجى إدخال اسم المستخدم وكلمة المرور."
            }), 400

        # البحث عن المشرف الأساسي أو موظف الإدارة
        admin = AdminUser.query.filter_by(username=username).first()
        if not admin:
            admin = AdminStaff.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            if hasattr(admin, 'is_active') and not admin.is_active:
                return jsonify({
                    "status": "error",
                    "message": "هذا الحساب معطل حالياً."
                }), 403

            session['admin_logged_in'] = True
            session['user_type'] = 'admin'
            session['_user_id'] = str(admin.id)
            
            return jsonify({
                "status": "success",
                "message": "تم المصادقة بنجاح، جاري التوجيه...",
                "redirect": url_for('auth_portal.dashboard')
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "اسم المستخدم أو كلمة المرور غير صحيحة."
            }), 401

    except Exception as e:
        print(f"❌ [خطأ تسجيل الدخول]: {traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": "حدث خطأ داخلي في الخادم السيادي."
        }), 500


@auth_portal.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in') and not session.get('_user_id'):
        return redirect(SECRET_ADMIN_PATH)
    return "مرحباً بك في لوحة التحكم السيادية الإدارية - محجوب أونلاين"
