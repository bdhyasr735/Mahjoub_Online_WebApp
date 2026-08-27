# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/routes.py

import os
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect
from flask_login import login_user, logout_user, login_required
from sqlalchemy import or_
from werkzeug.routing import BuildError

from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.suppliers_auth_portal.auth_service import SupplierAuthService

suppliers_bp = Blueprint('suppliers_auth', __name__, template_folder='templates')
auth_service = SupplierAuthService()


def get_wait_time(attempts):
    if attempts <= 5:
        return 0
    return 2 ** (attempts - 6)


@suppliers_bp.route('/test-login', methods=['GET', 'POST'])
def test_login():
    if request.method == 'GET':
        return '''
        <h2>🔍 اختبار الدخول لموردين المنصة</h2>
        <form method="POST" style="direction: rtl; font-family: Tahoma; padding: 20px;">
            <div style="margin-bottom: 10px;">
                <label>اسم المستخدم أو الهاتف:</label><br>
                <input type="text" name="username" placeholder="أدخل اسم المستخدم أو الهاتف" style="padding: 8px; width: 250px;">
            </div>
            <div style="margin-bottom: 10px;">
                <label>كلمة المرور:</label><br>
                <input type="password" name="password" placeholder="أدخل كلمة المرور" style="padding: 8px; width: 250px;">
            </div>
            <button type="submit" style="padding: 8px 20px; background: #2d0b36; color: #fff; border: none; border-radius: 5px;">دخول</button>
        </form>
        <hr>
        <p><strong>المستخدم الافتراضي:</strong> test_supplier / 123</p>
        '''

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    user = Supplier.query.filter(
        or_(Supplier.username == username, Supplier.search_phone == username)
    ).first()

    if not user:
        return f"""
        <div style="direction: rtl; font-family: Tahoma; padding: 20px;">
            <h2 style="color: #d9534f;">❌ المستخدم غير موجود</h2>
            <p>المستخدم <strong>'{username}'</strong> غير موجود في قاعدة بيانات الموردين.</p>
            <p>المستخدمون المسجلون:</p>
            <ul>
            {''.join([f"<li>{u.username} ({u.trade_name or 'بدون اسم تجاري'})</li>" for u in Supplier.query.all()])}
            </ul>
            <a href="/supplier/test-login">محاولة مرة أخرى</a>
        </div>
        """

    try:
        if user.check_password(password):
            return f"""
            <div style="direction: rtl; font-family: Tahoma; padding: 20px;">
                <h2 style="color: #28a745;">✅ كلمة المرور صحيحة!</h2>
                <p>المستخدم: <strong>{user.username}</strong></p>
                <p>المتجر: <strong>{user.trade_name or 'غير محدد'}</strong></p>
                <p>المعرف: <strong>{user.id}</strong></p>
                <br>
                <a href="/supplier/dashboard" style="background: #2d0b36; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px;">اذهب للداشبورد</a>
                <br><br>
                <a href="/supplier/test-login">رجوع</a>
            </div>
            """
        else:
            return f"""
            <div style="direction: rtl; font-family: Tahoma; padding: 20px;">
                <h2 style="color: #d9534f;">❌ كلمة المرور غير صحيحة</h2>
                <p>المستخدم: <strong>{user.username}</strong></p>
                <p>كلمة المرور المدخلة غير صحيحة.</p>
                <a href="/supplier/test-login">محاولة مرة أخرى</a>
            </div>
            """
    except Exception as e:
        return f"""
        <div style="direction: rtl; font-family: Tahoma; padding: 20px;">
            <h2 style="color: #d9534f;">❌ خطأ في التحقق</h2>
            <p><strong>{str(e)}</strong></p>
            <a href="/supplier/test-login">محاولة مرة أخرى</a>
        </div>
        """


@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/login.html')

    try:
        if request.is_json:
            json_data = request.get_json() or {}
            username = json_data.get('username', '').strip()
            password = json_data.get('password', '')
            step = json_data.get('step', 'credentials')
            entered_otp = json_data.get('otp_code', '').strip()
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            step = request.form.get('step', 'credentials')
            entered_otp = request.form.get('otp_code', '').strip()

        block_until = session.get('block_until')
        if block_until and datetime.now() < datetime.fromisoformat(block_until):
            remaining = int((datetime.fromisoformat(block_until) - datetime.now()).total_seconds() / 60) + 1
            msg = f"لا يمكنك المحاولة حالياً. يرجى الانتظار {remaining} دقيقة."
            if request.is_json:
                return jsonify({"status": "error", "message": msg}), 429
            return render_template('suppliers_auth_portal/login.html', error=msg)

        if step == 'verify_otp':
            stored_hash = session.get('pending_otp_hash')
            expires_at_str = session.get('pending_otp_expires')
            target_user_id = session.get('pending_user_id')
            found_as = session.get('pending_user_type')

            if not stored_hash or not expires_at_str or not target_user_id:
                msg = "انتهت صلاحية جلسة التحقق، يرجى إعادة تسجيل الدخول."
                if request.is_json:
                    return jsonify({"status": "error", "message": msg}), 400
                return render_template('suppliers_auth_portal/login.html', error=msg)

            if datetime.now() > datetime.fromisoformat(expires_at_str):
                session.pop('pending_otp_hash', None)
                session.pop('pending_otp_expires', None)
                session.pop('pending_user_id', None)
                msg = "انتهت صلاحية رمز التحقق (OTP)، يرجى طلب رمز جديد."
                if request.is_json:
                    return jsonify({"status": "error", "message": msg}), 400
                return render_template('suppliers_auth_portal/login.html', error=msg)

            if not auth_service.verify_otp_hash(entered_otp, stored_hash):
                msg = "رمز التحقق غير صحيح."
                if request.is_json:
                    return jsonify({"status": "error", "message": msg}), 400
                return render_template('suppliers_auth_portal/login.html', error=msg, require_otp=True)

            target_user = Supplier.query.get(target_user_id) if found_as == 'supplier' else SupplierStaff.query.get(target_user_id)
            if not target_user:
                msg = "حساب المستخدم غير موجود."
                if request.is_json:
                    return jsonify({"status": "error", "message": msg}), 404
                return render_template('suppliers_auth_portal/login.html', error=msg)

            session.pop('pending_otp_hash', None)
            session.pop('pending_otp_expires', None)
            session.pop('pending_user_id', None)
            session.pop('pending_user_type', None)

            session.permanent = True
            session['user_type'] = found_as
            session.pop('login_attempts', None)
            session.pop('block_until', None)

            login_user(target_user, remember=True)

            try:
                redirect_url = url_for('suppliers_dashboard.dashboard')
            except BuildError:
                redirect_url = '/supplier/dashboard'

            if request.is_json:
                return jsonify({"status": "success", "redirect": redirect_url})
            return redirect(redirect_url)

        target_user = Supplier.query.filter(
            or_(Supplier.search_phone == username, Supplier.username == username)
        ).first()
        found_as = 'supplier' if target_user else None

        if not target_user:
            target_user = SupplierStaff.query.filter(
                or_(SupplierStaff.search_phone == username, SupplierStaff.username == username)
            ).first()
            found_as = 'supplier_staff' if target_user else None

        if not target_user:
            msg = "المستخدم غير مسجل في منصة الموردين"
            if request.is_json:
                return jsonify({"status": "error", "message": msg}), 404
            return render_template('suppliers_auth_portal/login.html', error=msg)

        if not target_user.check_password(password.strip()):
            attempts = session.get('login_attempts', 0) + 1
            session['login_attempts'] = attempts
            if attempts >= 5:
                wait_minutes = get_wait_time(attempts)
                session['block_until'] = (datetime.now() + timedelta(minutes=wait_minutes)).isoformat()

            msg = "كلمة المرور غير صحيحة"
            if request.is_json:
                return jsonify({"status": "error", "message": msg}), 401
            return render_template('suppliers_auth_portal/login.html', error=msg)

        if hasattr(target_user, 'is_active') and not target_user.is_active:
            msg = "الحساب غير مفعل حالياً."
            if request.is_json:
                return jsonify({"status": "error", "message": msg}), 403
            return render_template('suppliers_auth_portal/login.html', error=msg)

        supplier_phone = getattr(target_user, 'search_phone', None) or getattr(target_user, 'phone', '')
        supplier_email = getattr(target_user, 'email', '')

        otp_result = auth_service.process_supplier_auth_otp(supplier_phone, supplier_email)

        if not otp_result["success"]:
            msg = "تعذر إرسال رمز التحقق عبر قنوات الاتصال، يرجى المحاولة لاحقاً."
            if request.is_json:
                return jsonify({"status": "error", "message": msg}), 500
            return render_template('suppliers_auth_portal/login.html', error=msg)

        session['pending_otp_hash'] = otp_result["hashed_otp"]
        session['pending_otp_expires'] = otp_result["expires_at"].isoformat()
        session['pending_user_id'] = target_user.id
        session['pending_user_type'] = found_as

        success_msg = f"تم إرسال رمز التحقق بنجاح عبر قناة ({otp_result['channel']})."
        if request.is_json:
            return jsonify({
                "status": "require_otp",
                "message": success_msg,
                "channel": otp_result["channel"]
            })
        
        return render_template('suppliers_auth_portal/login.html', require_otp=True, info=success_msg)

    except Exception as e:
        print(f"❌ [Supplier Login Error]: {str(e)}")
        msg = "حدث خطأ تقني في النظام أثناء تسجيل الدخول"
        if request.is_json:
            return jsonify({"status": "error", "message": msg}), 500
        return render_template('suppliers_auth_portal/login.html', error=msg)


@suppliers_bp.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('suppliers_auth.login'))


def fallback_standard_method(supplier_id):
    return {"status": "fallback", "data": [0.0]}


@suppliers_bp.route('/zsa-window/<int:supplier_id>', methods=['GET'])
@login_required
def supplier_zsa_window(supplier_id):
    sample_raw_data = [[10.0, 20.0], [30.0, 40.0], [50.0, 60.0]]

    try:
        from apps.zsa_engine.engine import zsa_core
        processed_results = zsa_core.process_window_data(sample_raw_data)

        return jsonify({
            "status": "success",
            "engine": "ZSA-State-Zero",
            "supplier_id": supplier_id,
            "results": processed_results
        }), 200

    except Exception as e:
        fallback_data = fallback_standard_method(supplier_id)
        return jsonify({
            "status": "recovered_via_fallback",
            "error": str(e),
            "data": fallback_data
        }), 200
