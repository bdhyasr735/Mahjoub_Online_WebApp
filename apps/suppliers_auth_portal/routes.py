# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect, flash
from flask_login import login_user, logout_user, login_required
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff

suppliers_bp = Blueprint('suppliers_auth', __name__, template_folder='templates')

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/login.html')

    try:
        data = request.get_json() or request.form.to_dict()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        # 1. محاولة البحث في المورد الرئيسي
        user = Supplier.query.filter(
            (Supplier.search_phone == username) | (Supplier.username == username)
        ).first()
        
        if user and user.check_password(password):
            session['user_type'] = 'supplier'
            login_user(user, remember=True)
            return jsonify({"status": "success", "redirect": url_for('suppliers_dashboard.dashboard')})

        # 2. البحث في جدول الموظفين
        staff = SupplierStaff.query.filter(
            (SupplierStaff.phone == username) | (SupplierStaff.username == username)
        ).first()

        if staff and staff.check_password(password):
            session['user_type'] = 'staff'
            login_user(staff, remember=True)
            return jsonify({"status": "success", "redirect": url_for('suppliers_dashboard.dashboard')})

        return jsonify({"status": "error", "message": "بيانات الدخول غير صحيحة"}), 401

    except Exception as e:
        return jsonify({"status": "error", "message": "حدث خطأ في النظام"}), 500

@suppliers_bp.route('/logout')
@login_required
def logout():
    """تسجيل خروج آمن يمسح الجلسة ونوع المستخدم"""
    session.pop('user_type', None) # مسح نوع المستخدم
    logout_user() # مسح بيانات Flask-Login
    session.clear() # تنظيف شامل للجلسة
    flash("تم تسجيل الخروج بنجاح.", "success")
    return redirect(url_for('suppliers_auth.login'))
