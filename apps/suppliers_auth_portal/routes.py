# coding: utf-8
# 📂 apps/suppliers_auth_portal/routes.py

from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect, flash
from flask_login import login_user, logout_user, login_required
from sqlalchemy import or_
from datetime import datetime, timedelta
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff

suppliers_bp = Blueprint('suppliers_auth', __name__, template_folder='templates')

def get_wait_time(attempts):
    if attempts <= 5: return 0
    return 2 ** (attempts - 6)

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/login.html')

    try:
        # دعم قراءة البيانات سواء أرسلت عن طريق JSON أو عن طريق Form Submission عادي
        if request.is_json:
            data = request.get_json() or {}
            username = data.get('username', '').strip()
            password = data.get('password', '')
            user_type = data.get('type')
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            user_type = request.form.get('type') # 'supplier' أو 'staff'

        # 1. التحقق من الحظر
        block_until = session.get('block_until')
        if block_until and datetime.now() < datetime.fromisoformat(block_until):
            remaining = int((datetime.fromisoformat(block_until) - datetime.now()).total_seconds() / 60) + 1
            msg = f"لا يمكنك المحاولة حالياً. يرجى الانتظار {remaining} دقيقة."
            return jsonify({"status": "error", "message": msg}), 429 if request.is_json else render_template('suppliers_auth_portal/login.html', error=msg)

        target_user = None
        found_as = None

        # 2. البحث الصارم في الجدول المحدد
        if user_type == 'supplier':
            target_user = Supplier.query.filter(or_(Supplier.search_phone == username, Supplier.username == username)).first()
            if target_user: found_as = 'supplier'
        elif user_type == 'staff':
            target_user = SupplierStaff.query.filter(or_(SupplierStaff.search_phone == username, SupplierStaff.username == username)).first()
            if target_user: found_as = 'staff'

        # 3. البحث المرن البديل في حال عدم المطابقة الفورية
        if not target_user:
            target_user = Supplier.query.filter(or_(Supplier.search_phone == username, Supplier.username == username)).first()
            if target_user:
                found_as = 'supplier'
            else:
                target_user = SupplierStaff.query.filter(or_(SupplierStaff.search_phone == username, SupplierStaff.username == username)).first()
                if target_user:
                    found_as = 'staff'

        # 4. إذا لم يتم العثور على الحساب
        if not target_user:
            msg = "المستخدم غير مسجل في المنصة اللامركزية"
            return jsonify({"status": "error", "message": msg}), 404 if request.is_json else render_template('suppliers_auth_portal/login.html', error=msg)

        # 5. التحقق من كلمة المرور
        if not target_user.check_password(password):
            attempts = session.get('login_attempts', 0) + 1
            session['login_attempts'] = attempts
            if attempts >= 5:
                wait_minutes = get_wait_time(attempts)
                session['block_until'] = (datetime.now() + timedelta(minutes=wait_minutes)).isoformat()
            
            msg = "كلمة المرور غير صحيحة"
            return jsonify({"status": "error", "message": msg}), 401 if request.is_json else render_template('suppliers_auth_portal/login.html', error=msg)

        # 6. التحقق من التفعيل
        if hasattr(target_user, 'is_active') and not target_user.is_active:
            # تم تخصيص الرسالة للموظف كما طلبت
            if found_as == 'staff':
                msg = "تم إيقاف المستخدم من قبل المتجر، يرجى مراجعة المتجر الأساسي."
            else:
                msg = "الحساب غير مفعل حالياً."
            return jsonify({"status": "error", "message": msg}), 403 if request.is_json else render_template('suppliers_auth_portal/login.html', error=msg)

        # 7. تسجيل الدخول وتثبيت الجلسة بشكل نهائي
        session.pop('login_attempts', None)
        session.pop('block_until', None)
        
        # تثبيت النوع الفعلي لمنع التداخل والدوران
        session['user_type'] = found_as
        
        # عمل تسجيل دخول رسمي في Flask-Login
        login_user(target_user, remember=True)
        
        # توليد رابط الوجهة الصحيح والمباشر
        redirect_url = url_for('suppliers_dashboard.dashboard')
        
        if request.is_json:
            return jsonify({"status": "success", "redirect": redirect_url})
        else:
            return redirect(redirect_url)

    except Exception as e:
        print(f"❌ [Login Error]: {str(e)}")
        msg = "حدث خطأ تقني في النظام"
        return jsonify({"status": "error", "message": msg}), 500 if request.is_json else render_template('suppliers_auth_portal/login.html', error=msg)

@suppliers_bp.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('suppliers_auth.login'))
