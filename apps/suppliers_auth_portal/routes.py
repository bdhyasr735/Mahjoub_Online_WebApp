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
# 🟣 مسار تسجيل الدخول الأساسي (مصحح لتجنب إعادة التوجيه الحلقي)
# ============================================================
@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/login.html')

    try:
        # قراءة البيانات سواء كانت JSON أو Form Data
        if request.is_json:
            json_data = request.get_json() or {}
            username = json_data.get('username', '').strip()
            password = json_data.get('password', '')
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

        # 1. التحقق من الحظر
        block_until = session.get('block_until')
        if block_until and datetime.now() < datetime.fromisoformat(block_until):
            remaining = int((datetime.fromisoformat(block_until) - datetime.now()).total_seconds() / 60) + 1
            msg = f"لا يمكنك المحاولة حالياً. يرجى الانتظار {remaining} دقيقة."
            if request.is_json:
                return jsonify({"status": "error", "message": msg}), 429
            return render_template('suppliers_auth_portal/login.html', error=msg)

        # 2. البحث الشامل في الجدولين
        target_user = Supplier.query.filter(or_(Supplier.search_phone == username, Supplier.username == username)).first()
        found_as = 'supplier' if target_user else None

        if not target_user:
            target_user = SupplierStaff.query.filter(or_(SupplierStaff.search_phone == username, SupplierStaff.username == username)).first()
            found_as = 'staff' if target_user else None

        # 3. التحقق من وجود المستخدم
        if not target_user:
            msg = "المستخدم غير مسجل في المنصة اللامركزية"
            if request.is_json:
                return jsonify({"status": "error", "message": msg}), 404
            return render_template('suppliers_auth_portal/login.html', error=msg)

        # 4. التحقق من كلمة المرور
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

        # 5. التحقق من التفعيل
        if hasattr(target_user, 'is_active') and not target_user.is_active:
            msg = "الحساب غير مفعل حالياً."
            if request.is_json:
                return jsonify({"status": "error", "message": msg}), 403
            return render_template('suppliers_auth_portal/login.html', error=msg)

        # 6. تثبيت الجلسة وتسجيل الدخول بنجاح
        session.permanent = True
        session['user_type'] = found_as
        
        # تفريغ عداد محاولات الدخول الفاشلة
        session.pop('login_attempts', None)
        session.pop('block_until', None)

        login_user(target_user, remember=True)
        
        redirect_url = url_for('suppliers_dashboard.dashboard')
        
        # إذا كان الطلب AJAX/JSON نرجع رابط التحويل، وإلا نعمل Redirect مباشر للمتصفح
        if request.is_json:
            return jsonify({"status": "success", "redirect": redirect_url})
            
        return redirect(redirect_url)

    except Exception as e:
        print(f"❌ [Login Error]: {str(e)}")
        msg = "حدث خطأ تقني في النظام"
        if request.is_json:
            return jsonify({"status": "error", "message": msg}), 500
        return render_template('suppliers_auth_portal/login.html', error=msg)


# ============================================================
# 🟣 مسار تسجيل الخروج
# ============================================================
@suppliers_bp.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('suppliers_auth.login'))


# ============================================================
# ⚡ نافذة اختبار معمارية الحالة الصفرية المستقلة (ZSA Engine Window)
# ============================================================
from apps.zsa_engine.engine import zsa_core

def fallback_standard_method(supplier_id):
    return {"status": "fallback", "data": [0.0]}

@suppliers_bp.route('/supplier/zsa-window/<int:supplier_id>', methods=['GET'])
@login_required
def supplier_zsa_window(supplier_id):
    sample_raw_data = [[10.0, 20.0], [30.0, 40.0], [50.0, 60.0]]
    
    try:
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
