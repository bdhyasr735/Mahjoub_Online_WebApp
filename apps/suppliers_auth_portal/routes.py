# coding: utf-8
# 📂 apps/suppliers_auth_portal/routes.py

from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect
from flask_login import login_user, logout_user, login_required
from sqlalchemy import or_
from datetime import datetime, timedelta
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff

# ✅ تعريف الـ Blueprint بالاسم الصحيح
suppliers_bp = Blueprint('suppliers_auth', __name__, template_folder='templates')

def get_wait_time(attempts):
    if attempts <= 5: return 0
    return 2 ** (attempts - 6)

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/login.html')

    try:
        # مسح الجلسة السابقة لضمان عدم وجود تداخل
        session.clear()

        # قراءة البيانات
        username = request.form.get('username', '').strip() if not request.is_json else request.get_json().get('username', '').strip()
        password = request.form.get('password', '') if not request.is_json else request.get_json().get('password', '')

        # 1. التحقق من الحظر
        block_until = session.get('block_until')
        if block_until and datetime.now() < datetime.fromisoformat(block_until):
            remaining = int((datetime.fromisoformat(block_until) - datetime.now()).total_seconds() / 60) + 1
            msg = f"لا يمكنك المحاولة حالياً. يرجى الانتظار {remaining} دقيقة."
            return jsonify({"status": "error", "message": msg}), 429 if request.is_json else render_template('suppliers_auth_portal/login.html', error=msg)

        # 2. البحث الشامل في الجدولين
        target_user = Supplier.query.filter(or_(Supplier.search_phone == username, Supplier.username == username)).first()
        found_as = 'supplier' if target_user else None

        if not target_user:
            target_user = SupplierStaff.query.filter(or_(SupplierStaff.search_phone == username, SupplierStaff.username == username)).first()
            found_as = 'staff' if target_user else None

        # 3. التحقق من وجود المستخدم
        if not target_user:
            msg = "المستخدم غير مسجل في المنصة اللامركزية"
            return jsonify({"status": "error", "message": msg}), 404 if request.is_json else render_template('suppliers_auth_portal/login.html', error=msg)

        # 4. التحقق من كلمة المرور
        if not target_user.check_password(password.strip()):
            attempts = session.get('login_attempts', 0) + 1
            session['login_attempts'] = attempts
            if attempts >= 5:
                wait_minutes = get_wait_time(attempts)
                session['block_until'] = (datetime.now() + timedelta(minutes=wait_minutes)).isoformat()
            
            msg = "كلمة المرور غير صحيحة"
            return jsonify({"status": "error", "message": msg}), 401 if request.is_json else render_template('suppliers_auth_portal/login.html', error=msg)

        # 5. التحقق من التفعيل
        if hasattr(target_user, 'is_active') and not target_user.is_active:
            msg = "الحساب غير مفعل حالياً."
            return jsonify({"status": "error", "message": msg}), 403 if request.is_json else render_template('suppliers_auth_portal/login.html', error=msg)

        # 6. تسجيل الدخول
        session['user_type'] = found_as
        login_user(target_user, remember=True)
        
        redirect_url = url_for('suppliers_dashboard.dashboard')
        return jsonify({"status": "success", "redirect": redirect_url}) if request.is_json else redirect(redirect_url)

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
