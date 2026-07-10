# coding: utf-8
# 📂 apps/suppliers_auth_portal/routes.py

from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect
from flask_login import login_user, logout_user, login_required
from sqlalchemy import or_
from datetime import datetime, timedelta
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff

suppliers_bp = Blueprint('suppliers_auth', __name__, template_folder='templates')

def get_wait_time(attempts):
    """حساب وقت الانتظار: يبدأ من دقيقة ويتضاعف (1، 2، 4، 8...)"""
    if attempts <= 5: return 0
    return 2 ** (attempts - 6)

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/login.html')

    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        password = data.get('password', '')

        # 1. التحقق من حالة الحظر
        block_until = session.get('block_until')
        if block_until and datetime.now() < datetime.fromisoformat(block_until):
            remaining = int((datetime.fromisoformat(block_until) - datetime.now()).total_seconds() / 60) + 1
            return jsonify({"status": "error", "message": f"لا يمكنك المحاولة حالياً. يرجى الانتظار {remaining} دقيقة."}), 429

        # 2. البحث عن المستخدم
        user = Supplier.query.filter(or_(Supplier.search_phone == username, Supplier.username == username)).first()
        staff = None
        if not user:
            staff = SupplierStaff.query.filter(or_(SupplierStaff.search_phone == username, SupplierStaff.username == username)).first()

        # 3. التحقق من وجود المستخدم
        if not user and not staff:
            return jsonify({"status": "error", "message": "عذراً، هذا المستخدم غير مسجل في المنصة اللامركزية"}), 404

        target_user = user or staff

        # 4. التحقق من كلمة المرور
        if not target_user.check_password(password):
            attempts = session.get('login_attempts', 0) + 1
            session['login_attempts'] = attempts
            
            if attempts >= 5:
                wait_minutes = get_wait_time(attempts)
                session['block_until'] = (datetime.now() + timedelta(minutes=wait_minutes)).isoformat()
            
            return jsonify({"status": "error", "message": "كلمة المرور غير صحيحة"}), 401

        # 5. التحقق من حالة التفعيل
        if hasattr(target_user, 'is_active') and not target_user.is_active:
            return jsonify({"status": "error", "message": "بيانات دخول صحيحة ولكن الحساب غير مفعل"}), 403

        # 6. نجاح الدخول
        session.pop('login_attempts', None)
        session.pop('block_until', None)
        session['user_type'] = 'supplier' if user else 'staff'
        login_user(target_user, remember=True)
        return jsonify({"status": "success", "redirect": url_for('suppliers_dashboard.dashboard')})

    except Exception as e:
        print(f"❌ [Login Error]: {str(e)}")
        return jsonify({"status": "error", "message": "حدث خطأ تقني في النظام"}), 500

@suppliers_bp.route('/logout')
@login_required
def logout():
    """تسجيل خروج المستخدم ومسح الجلسة بالكامل."""
    session.clear()
    logout_user()
    return redirect(url_for('suppliers_auth.login'))
