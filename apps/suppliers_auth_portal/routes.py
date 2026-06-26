# coding: utf-8
# 📂 apps/suppliers_auth_portal/routes.py - نظام الدخول المباشر للموردين والمسوقين

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from apps.models.supplier_db import Supplier
from apps.models.marketer_db import Marketer # تأكد من صحة مسار الاستيراد

# تعريف الـ Blueprint باسم 'suppliers' ليتطابق مع ما تستخدمه في url_for
suppliers_bp = Blueprint('suppliers', __name__, template_folder='templates')

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    # في حالة الطلب العادي (GET) نعرض صفحة تسجيل الدخول
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('suppliers.dashboard'))
        return render_template('suppliers_auth_portal/login.html')

    # في حالة طلب تسجيل الدخول (POST)
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
                return jsonify({"status": "success", "redirect": url_for('suppliers.dashboard')})
            return jsonify({"status": "error", "message": "بيانات دخول المسوق غير صحيحة"}), 401

        # --- منطق دخول الموردين ---
        if login_type == 'supplier':
            # البحث باستخدام الهاتف أو اسم المستخدم
            supplier = Supplier.query.filter(
                (Supplier.search_phone == username) | (Supplier.username == username)
            ).first()
            
            if supplier and supplier.check_password(password):
                login_user(supplier, remember=True)
                return jsonify({"status": "success", "redirect": url_for('suppliers.dashboard')})
            return jsonify({"status": "error", "message": "بيانات دخول المورد غير صحيحة"}), 401

        return jsonify({"status": "error", "message": "نوع دخول غير معروف"}), 400

    except Exception as e:
        print(f"🚨 [Error] Login failed: {str(e)}")
        return jsonify({"status": "error", "message": "خطأ فني في النظام"}), 500

@suppliers_bp.route('/dashboard')
@login_required
def dashboard():
    return "مرحباً بك في لوحة تحكم الشركاء لمنصة محجوب أونلاين"

@suppliers_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('suppliers.login'))
