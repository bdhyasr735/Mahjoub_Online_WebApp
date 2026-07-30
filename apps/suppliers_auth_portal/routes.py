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


# ============================================================
# 🔍 مسار اختبار الدخول (للتشخيص)
# ============================================================
@suppliers_bp.route('/test-login', methods=['GET', 'POST'])
def test_login():
    if request.method == 'GET':
        return '''
        <h2>🔍 اختبار الدخول</h2>
        <form method="POST" style="direction: rtl; font-family: Tahoma; padding: 20px;">
            <div style="margin-bottom: 10px;">
                <label>اسم المستخدم:</label><br>
                <input type="text" name="username" placeholder="أدخل اسم المستخدم" style="padding: 8px; width: 250px;">
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
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    # البحث عن المستخدم
    user = Supplier.query.filter_by(username=username).first()
    
    if not user:
        return f"""
        <div style="direction: rtl; font-family: Tahoma; padding: 20px;">
            <h2 style="color: #d9534f;">❌ المستخدم غير موجود</h2>
            <p>المستخدم <strong>'{username}'</strong> غير موجود في قاعدة البيانات.</p>
            <p>المستخدمون المسجلون:</p>
            <ul>
            {''.join([f"<li>{u.username}</li>" for u in Supplier.query.all()])}
            </ul>
            <a href="/supplier/test-login">محاولة مرة أخرى</a>
        </div>
        """
    
    # التحقق من كلمة المرور
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


# ============================================================
# 🟣 مسار تسجيل الدخول الأساسي
# ============================================================
@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/login.html')

    try:
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


# ============================================================
# 🟣 مسار تسجيل الخروج
# ============================================================
@suppliers_bp.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('suppliers_auth.login'))
