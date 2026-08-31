# -*- coding: utf-8 -*-
# 📂 apps/auth_portal/routes.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, abort
from apps.models.admin_db import AdminUser
from apps.models.admin_staff_db import AdminStaff
import traceback

auth_portal = Blueprint('auth_portal', __name__, template_folder='templates')
auth_portal_bp = auth_portal

SECRET_ADMIN_PATH = '/m7jb_sovereign_hq_v2_99x'

@auth_portal.route(SECRET_ADMIN_PATH, methods=['GET', 'POST'])
def secure_admin_login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    try:
        # التأكد من استقبال البيانات بصيغة JSON
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "status": "error",
                "message": "بيانات الطلب غير صالحة."
            }), 400

        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                "status": "error",
                "message": "يرجى إدخال اسم المستخدم وكلمة المرور."
            }), 400

        # البحث عن المستخدم الإداري
        admin = AdminUser.query.filter_by(username=username).first()
        if not admin:
            admin = AdminStaff.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            if not admin.is_active:
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
        # طباعة الخطأ في السجلات لمراجعته إذا ظهرت المشكلة مجدداً
        print(f"Login Error: {traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": "حدث خطأ داخلي في الخادم السيادي."
        }), 500


@auth_portal.route('/login', methods=['GET', 'POST'])
def fake_login():
    abort(404)


@auth_portal.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in') and not session.get('_user_id'):
        return redirect(SECRET_ADMIN_PATH)
    
    return "مرحباً بك في لوحة التحكم السيادية الإدارية - محجوب أونلاين"
