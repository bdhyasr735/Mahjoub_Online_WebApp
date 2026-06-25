# coding: utf-8
# 📂 apps/suppliers_auth_portal/routes.py - نظام الدخول المباشر للموردين والمسوقين

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, current_user
from apps.extensions import db  
from apps.models import Supplier, Marketer

suppliers_bp = Blueprint('suppliers', __name__, template_folder='templates')

@suppliers_bp.before_request
def check_login():
    # حماية المسارات: استثناء صفحة الدخول
    if request.endpoint in ['suppliers.login', 'static']:
        return None
    if not current_user.is_authenticated and request.blueprint == 'suppliers':
        return redirect(url_for('suppliers.login'))

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('suppliers.dashboard'))
        return render_template('suppliers_auth_portal/login.html')

    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "بيانات غير صالحة"}), 400

        login_type = data.get('type')
        username = data.get('username', '').strip()
        password = data.get('password', '')

        # --- منطق دخول المسوقين ---
        if login_type == 'marketer':
            user = Marketer.query.filter_by(marketing_code=username).first()
            if user and user.check_password(password):
                login_user(user, remember=True)
                return jsonify({"status": "success", "redirect": url_for('marketers.dashboard')})
            return jsonify({"status": "error", "message": "بيانات دخول المسوق غير صحيحة"}), 401

        # --- منطق دخول الموردين ---
        if login_type == 'supplier':
            # البحث عن المورد بالهاتف أو باسم المستخدم
            supplier = Supplier.query.filter((Supplier.phone == username) | (Supplier.username == username)).first()
            
            # ملاحظة: تأكد أن المودل يحتوي على check_password أو مقارنة مباشرة حسب نظام تشفيرك
            if supplier and supplier.check_password(password):
                login_user(supplier, remember=True)
                return jsonify({"status": "success", "redirect": url_for('suppliers.dashboard')})
            return jsonify({"status": "error", "message": "بيانات دخول المورد غير صحيحة"}), 401

        return jsonify({"status": "error", "message": "نوع دخول غير معروف"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": "خطأ فني في النظام"}), 500

@suppliers_bp.route('/dashboard')
def dashboard():
    return "مرحباً بك في لوحة تحكم الموردين لمنصة محجوب أونلاين"

@suppliers_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('suppliers.login'))
