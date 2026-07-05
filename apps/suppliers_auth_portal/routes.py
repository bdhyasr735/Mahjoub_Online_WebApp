# coding: utf-8
# 📂 apps/suppliers_auth_portal/routes.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, make_response
from flask_login import login_user, logout_user, login_required, current_user
from apps.models.supplier_db import Supplier
from apps.models.marketer_db import Marketer

# تعريف الـ Blueprint
suppliers_bp = Blueprint('suppliers_auth', __name__, template_folder='templates')

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():# coding: utf-8
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
    بوابة تسجيل دخول الموردين والمسوقين المحسنة.
    """
    if request.method == 'GET':
        # التحقق من أن المستخدم غير مسجل دخول بالفعل لمنع التوجيه الخاطئ
        if current_user.is_authenticated and session.get('user_type') == 'supplier':
            return redirect(url_for('suppliers_dashboard.dashboard'))
        return render_template('suppliers_auth_portal/login.html')

    try:
        # التعديل الجوهري: دعم JSON (للطلبات عبر JS) والـ Form Data (للطلبات التقليدية)
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        if not data:
            return jsonify({"status": "error", "message": "لم يتم إرسال بيانات"}), 400

        login_type = data.get('type', 'supplier') 
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({"status": "error", "message": "يجب إدخال اسم المستخدم وكلمة المرور"}), 400

        # --- منطق دخول المسوقين ---
        if login_type == 'marketer':
            user = Marketer.query.filter_by(marketing_code=username).first()
            if user and user.check_password(password):
                login_user(user, remember=True)
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
                session['user_type'] = 'supplier'
                session.modified = True
                return jsonify({"status": "success", "redirect": url_for('suppliers_dashboard.dashboard')})
            return jsonify({"status": "error", "message": "بيانات دخول المورد غير صحيحة"}), 401

        return jsonify({"status": "error", "message": "نوع دخول غير معروف"}), 400

    except Exception as e:
        # هذا الجزء سيساعدك الآن في رؤية الخطأ الحقيقي في المتصفح إذا حدث استثناء
        return jsonify({"status": "error", "message": f"خطأ فني داخلي: {str(e)}"}), 500

@suppliers_bp.route('/logout')
def logout():
    """
    تسجيل خروج آمن.
    """
    logout_user()
    session.clear() 
    response = make_response(redirect(url_for('suppliers_auth.login')))
    response.set_cookie('session', '', expires=0, path='/')
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
    """
    بوابة تسجيل دخول الموردين والمسوقين.
    """
    if request.method == 'GET':
        # التحقق من أن المستخدم غير مسجل دخول بالفعل لمنع التوجيه الخاطئ
        if current_user.is_authenticated and session.get('user_type') == 'supplier':
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
    تسجيل خروج آمن: يقوم بمسح الجلسة تماماً وإجبار المتصفح على عدم التخزين المؤقت.
    """
    # 1. تسجيل الخروج من Flask-Login
    logout_user()
    
    # 2. إفراغ محتويات الجلسة
    session.clear() 
    
    # 3. إعداد الاستجابة لمنع التخزين المؤقت (Cache) في المتصفح
    response = make_response(redirect(url_for('suppliers_auth.login')))
    
    # 4. مسح الكوكي الخاص بالجلسة نهائياً من المتصفح
    response.set_cookie('session', '', expires=0, path='/')
    
    # 5. تعيين رؤوس أمنية صارمة لمنع التخزين المؤقت
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response
