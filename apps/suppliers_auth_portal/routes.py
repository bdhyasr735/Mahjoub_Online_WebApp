# coding: utf-8
# 📂 apps/suppliers_auth_portal/routes.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, make_response
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
                session.modified = True
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
                session.modified = True
                return jsonify({"status": "success", "redirect": url_for('suppliers_dashboard.dashboard')})
            return jsonify({"status": "error", "message": "بيانات دخول المورد غير صحيحة"}), 401

        return jsonify({"status": "error", "message": "نوع دخول غير معروف"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": f"خطأ فني: {str(e)}"}), 500

@suppliers_bp.route('/logout')
def logout():
    """
    تسجيل خروج آمن: إزالة كافة بيانات الجلسة وإخبار المتصفح بإلغاء التخزين المؤقت.
    هذا يمنع ظهور خطأ 403 عند محاولة العودة لصفحات محمية بعد الخروج.
    """
    # 1. تسجيل الخروج من Flask-Login
    logout_user()
    
    # 2. مسح كامل للجلسة من السيرفر
    session.clear() 
    
    # 3. إنشاء استجابة مع إعدادات منع التخزين المؤقت
    response = make_response(redirect(url_for('suppliers_auth.login')))
    
    # 4. إخبار المتصفح بمسح الكوكي
    response.set_cookie('session', '', expires=0)
    
    # 5. رؤوس أمنية لمنع المتصفح من تخزين الصفحة
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response
