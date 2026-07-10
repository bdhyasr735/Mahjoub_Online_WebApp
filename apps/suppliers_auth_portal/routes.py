# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect, flash
from flask_login import login_user, logout_user, login_required
from sqlalchemy import or_  # [تعديل هام] لاستبدال المعامل |
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff

suppliers_bp = Blueprint('suppliers_auth', __name__, template_folder='templates')

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/login.html')

    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        password = data.get('password', '')
        user_type = data.get('type')  # الحصول على نوع المستخدم من الفرونت إند

        dashboard_url = url_for('suppliers_dashboard.dashboard')

        # 1. حالة دخول المورد أو الموظف
        if user_type == 'supplier':
            user = Supplier.query.filter(
                or_(Supplier.search_phone == username, Supplier.username == username)
            ).first()
            if user and user.check_password(password):
                session.clear()
                session['user_type'] = 'supplier'
                session.permanent = True
                login_user(user, remember=True)
                return jsonify({"status": "success", "redirect": dashboard_url})

        # 2. حالة دخول الموظف
        elif user_type == 'staff':
            staff = SupplierStaff.query.filter(
                or_(SupplierStaff.phone == username, SupplierStaff.username == username)
            ).first()
            if staff and staff.check_password(password):
                session.clear()
                session['user_type'] = 'staff'
                session.permanent = True
                login_user(staff, remember=True)
                return jsonify({"status": "success", "redirect": dashboard_url})

        return jsonify({"status": "error", "message": "بيانات الدخول غير صحيحة"}), 401

    except Exception as e:
        print(f"❌ [Login Error]: {str(e)}")
        return jsonify({"status": "error", "message": "حدث خطأ تقني في النظام"}), 500

@suppliers_bp.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('suppliers_auth.login'))
