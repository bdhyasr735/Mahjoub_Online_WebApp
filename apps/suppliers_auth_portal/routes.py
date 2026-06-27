# coding: utf-8
# 📂 apps/suppliers_auth_portal/routes.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from apps.models.supplier_db import Supplier
from apps.models.marketer_db import Marketer

# تعريف الـ Blueprint
suppliers_bp = Blueprint('suppliers_auth', __name__, template_folder='templates')

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    بوابة تسجيل دخول الموردين والمسوقين.
    تستخدم session['user_type'] للتمييز بين أنواع المستخدمين في النظام.
    """
    if request.method == 'GET':
        # إذا كان المستخدم مسجلاً بالفعل، يتم توجيهه للداشبورد مباشرة
        if current_user.is_authenticated:
            return redirect(url_for('suppliers_dashboard.dashboard'))
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
                # تخزين نوع المستخدم في الجلسة للفصل الأمني
                session['user_type'] = 'supplier' 
                return jsonify({"status": "success", "redirect": url_for('suppliers_dashboard.dashboard')})
            return jsonify({"status": "error", "message": "بيانات دخول المسوق غير صحيحة"}), 401

        # --- منطق دخول الموردين ---
        if login_type == 'supplier':
            supplier = Supplier.query.filter(
                (Supplier.search_phone == username) | (Supplier.username == username)
            ).first()
            
            if supplier and supplier.check_password(password):
                login_user(supplier, remember=True)
                # تخزين نوع المستخدم في الجلسة للفصل الأمني
                session['user_type'] = 'supplier'
                return jsonify({"status": "success", "redirect": url_for('suppliers_dashboard.dashboard')})
            return jsonify({"status": "error", "message": "بيانات دخول المورد غير صحيحة"}), 401

        return jsonify({"status": "error", "message": "نوع دخول غير معروف"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": f"خطأ فني: {str(e)}"}), 500

@suppliers_bp.route('/logout')
@login_required
def logout():
    """
    تسجيل خروج المورد/المسوق مع التأكد من نوع الجلسة 
    لضمان الفصل الأمني الكامل وعدم التداخل مع الإدارة.
    """
    # التحقق من أن الجلسة الحالية تخص مورد أو مسوق فقط
    if session.get('user_type') == 'supplier':
        logout_user()
        session.clear() # مسح شامل للجلسة
    
    # التوجيه لبوابة دخول الموردين
    return redirect(url_for('suppliers_auth.login'))
