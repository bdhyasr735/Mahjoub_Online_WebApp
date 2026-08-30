# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/routes.py

from flask import render_template, request
from apps.suppliers_auth_portal import suppliers_bp
from apps.suppliers_auth_portal.auth_register import register_supplier_logic
from apps.suppliers_auth_portal.auth_login import login_supplier_logic
from apps.suppliers_auth_portal.auth_recovery import request_otp_logic, reset_password_logic

@suppliers_bp.route('/register', methods=['GET', 'POST'])
def register():
    """مسار عرض نموذج تسجيل المورد الجديد أو معالجة طلب التسجيل"""
    if request.method == 'POST':
        return register_supplier_logic()
    return render_template('suppliers_auth_portal/register.html')

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    """مسار تسجيل الدخول للموردين"""
    if request.method == 'POST':
        return login_supplier_logic()
    return render_template('suppliers_auth_portal/login.html')

@suppliers_bp.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    """عرض صفحة استعادة كلمة المرور ذات المرحلتين"""
    return render_template('suppliers_auth_portal/forgot_password.html')

@suppliers_bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """معالجة طلب وإرسال رمز التحقق OTP"""
    return request_otp_logic()

@suppliers_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """معالجة التحقق من الرمز وتحديث كلمة المرور"""
    return reset_password_logic()
