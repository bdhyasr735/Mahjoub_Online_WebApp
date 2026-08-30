# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_login.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from datetime import datetime

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff

bp = Blueprint('auth_login', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('suppliers_dashboard.dashboard'))
    
    if request.method == 'GET':
        # ✅ صفحة تسجيل دخول مدمجة (بدون قوالب)
        return """
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>بوابة الموردين - محجوب أونلاين</title>
            <style>
                * { box-sizing: border-box; }
                body { font-family: 'Segoe UI', Arial, sans-serif; background: #05020a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
                .card { background: #0f071c; border: 1px solid #ce9e49; border-radius: 20px; padding: 40px; max-width: 420px; width: 100%; box-shadow: 0 20px 60px rgba(0,0,0,0.8); }
                .logo { text-align: center; margin-bottom: 30px; }
                .logo h1 { font-size: 26px; margin: 0; background: linear-gradient(135deg, #ce9e49, #fae19c, #ce9e49); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
                .logo span { display: inline-block; background: rgba(206,158,73,0.2); color: #fae19c; padding: 2px 12px; border-radius: 20px; font-size: 10px; border: 1px solid rgba(206,158,73,0.3); }
                .logo p { color: #ce9e49; font-size: 14px; margin: 5px 0 0; }
                .input-group { margin-bottom: 18px; }
                label { display: block; margin-bottom: 6px; color: #ce9e49; font-size: 13px; font-weight: 600; }
                input { width: 100%; padding: 14px 16px; border-radius: 12px; border: 1px solid rgba(206,158,73,0.25); background: rgba(15,7,28,0.9); color: #fff; font-size: 15px; transition: all 0.3s; }
                input:focus { border-color: #ce9e49; outline: none; box-shadow: 0 0 20px rgba(206,158,73,0.15); }
                input::placeholder { color: rgba(255,255,255,0.3); }
                .btn { width: 100%; padding: 16px; background: linear-gradient(135deg, #ce9e49, #ba8b38); color: #05020a; border: none; border-radius: 12px; font-weight: 700; font-size: 16px; cursor: pointer; transition: all 0.3s; }
                .btn:hover { background: linear-gradient(135deg, #fae19c, #ce9e49); box-shadow: 0 0 30px rgba(206,158,73,0.3); }
                .btn:disabled { opacity: 0.6; cursor: not-allowed; }
                .alert { padding: 12px 16px; border-radius: 10px; margin-bottom: 16px; display: none; font-size: 14px; }
                .alert-error { background: rgba(220,38,38,0.15); border: 1px solid rgba(220,38,38,0.3); color: #fca5a5; }
                .alert-success { background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.3); color: #86efac; }
                .links { text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(206,158,73,0.1); font-size: 13px; }
                .links a { color: #ce9e49; text-decoration: none; margin: 0 8px; }
                .links a:hover { text-decoration: underline; }
                .footer { text-align: center; margin-top: 16px; font-size: 11px; color: #444; }
                .spinner { display: inline-block; width: 16px; height: 16px; border: 2px solid #05020a; border-top-color: transparent; border-radius: 50%; animation: spin 0.6s linear infinite; vertical-align: middle; margin-right: 8px; }
                @keyframes spin { to { transform: rotate(360deg); } }
                .tabs { display: flex; gap: 6px; background: rgba(15,7,28,0.6); padding: 4px; border-radius: 12px; margin-bottom: 24px; border: 1px solid rgba(206,158,73,0.1); }
                .tab { flex: 1; padding: 10px; text-align: center; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.3s; color: #666; background: transparent; border: none; }
                .tab.active { background: #ce9e49; color: #05020a; }
                .tab:hover:not(.active) { color: #ce9e49; }
            </style>
        </head>
        <body>
            <div class="card">
                <div class="logo">
                    <div style="font-size:48px;">🛒</div>
                    <h1>محجوب أونلاين <span>سوقك الذكي</span></h1>
                    <p>بوابة الموردين وموظفيهم</p>
                </div>
                
                <div class="tabs">
                    <button class="tab active" onclick="setType('supplier', this)">حساب المورد</button>
                    <button class="tab" onclick="setType('employee', this)">موظف المورد</button>
                </div>
                
                <div id="alertBox" class="alert"></div>
                
                <form id="loginForm">
                    <input type="hidden" id="userType" value="supplier">
                    <div class="input-group">
                        <label>رقم الهاتف أو البريد الإلكتروني</label>
                        <input type="text" id="identifier" placeholder="مثال: 77xxxxxxx أو البريد" value="test_supplier">
                    </div>
                    <div class="input-group">
                        <label>كلمة المرور</label>
                        <input type="password" id="password" placeholder="••••••••" value="123">
                    </div>
                    <button type="submit" class="btn" id="submitBtn">دخول المنظومة</button>
                </form>
                
                <div class="links">
                    <a href="/suppliers/register">اشتراك مورد جديد</a>
                    <span style="color:#444;">|</span>
                    <a href="/suppliers/forgot-password">نسيت كلمة المرور؟</a>
                </div>
                
                <div class="footer">🔒 مشفر 256-bit SSL | CSRF Protected</div>
            </div>
            
            <script>
                function setType(type, btn) {
                    document.getElementById('userType').value = type;
                    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                    btn.classList.add('active');
                }
                
                document.getElementById('loginForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    const identifier = document.getElementById('identifier').value.trim();
                    const password = document.getElementById('password').value;
                    const userType = document.getElementById('userType').value;
                    const alertBox = document.getElementById('alertBox');
                    const submitBtn = document.getElementById('submitBtn');
                    
                    alertBox.style.display = 'none';
                    alertBox.className = 'alert';
                    
                    if (!identifier || !password) {
                        alertBox.textContent = '⚠️ يرجى إدخال جميع البيانات';
                        alertBox.className = 'alert alert-error';
                        alertBox.style.display = 'block';
                        return;
                    }
                    
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<span class="spinner"></span> جاري التحقق...';
                    
                    try {
                        const response = await fetch('/suppliers/login', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ identifier, password, user_type: userType, remember_me: true })
                        });
                        const data = await response.json();
                        
                        if (data.success) {
                            alertBox.textContent = '✅ ' + data.message;
                            alertBox.className = 'alert alert-success';
                            alertBox.style.display = 'block';
                            setTimeout(() => { window.location.href = data.redirect_url; }, 1000);
                        } else {
                            alertBox.textContent = '❌ ' + data.message;
                            alertBox.className = 'alert alert-error';
                            alertBox.style.display = 'block';
                            submitBtn.disabled = false;
                            submitBtn.textContent = 'دخول المنظومة';
                        }
                    } catch(err) {
                        alertBox.textContent = '❌ خطأ في الاتصال بالخادم';
                        alertBox.className = 'alert alert-error';
                        alertBox.style.display = 'block';
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'دخول المنظومة';
                    }
                });
            </script>
        </body>
        </html>
        """
    
    # POST: معالجة تسجيل الدخول
    try:
        data = request.get_json() or request.form
        identifier = data.get('identifier', '').strip()
        password = data.get('password', '')
        user_type = data.get('user_type', 'supplier')
        remember_me = data.get('remember_me', False)
        
        if not identifier or not password:
            return jsonify({'success': False, 'message': 'يرجى إدخال جميع البيانات'}), 400
        
        search_phone = extract_phone_digits(identifier)
        user = None
        
        if user_type == 'supplier':
            user = Supplier.query.filter(
                or_(
                    Supplier.username == identifier,
                    Supplier.email == identifier,
                    Supplier.search_phone == search_phone
                )
            ).first()
        elif user_type == 'employee':
            user = SupplierStaff.query.filter(
                or_(
                    SupplierStaff.username == identifier,
                    SupplierStaff.search_phone == search_phone
                )
            ).first()
            if not user and '@' in identifier:
                all_staff = SupplierStaff.query.all()
                for staff in all_staff:
                    if staff.email and staff.email == identifier:
                        user = staff
                        break
        else:
            return jsonify({'success': False, 'message': 'نوع المستخدم غير مدعوم'}), 400
        
        if not user:
            return jsonify({'success': False, 'message': 'بيانات الدخول غير صحيحة'}), 401
        
        if user.status != 'active':
            return jsonify({'success': False, 'message': f'الحساب {user.status}'}), 403
        
        if not user.check_password(password):
            return jsonify({'success': False, 'message': 'بيانات الدخول غير صحيحة'}), 401
        
        login_user(user, remember=remember_me)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'redirect_url': url_for('suppliers_dashboard.dashboard'),
            'user': {'id': user.id, 'username': user.username, 'user_type': user_type, 'status': user.status}
        })
        
    except Exception as e:
        current_app.logger.error(f'❌ خطأ في تسجيل الدخول: {str(e)}')
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ في الخادم'}), 500


@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    username = current_user.username
    logout_user()
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('auth_login.login'))


def extract_phone_digits(value):
    if not value:
        return None
    digits = ''.join(filter(str.isdigit, str(value)))
    return digits[-9:] if len(digits) >= 9 else digits


@bp.errorhandler(401)
def unauthorized_error(error):
    if request.is_json:
        return jsonify({'success': False, 'message': 'يرجى تسجيل الدخول أولاً'}), 401
    flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
    return redirect(url_for('auth_login.login'))


@bp.errorhandler(403)
def forbidden_error(error):
    if request.is_json:
        return jsonify({'success': False, 'message': 'لا تملك صلاحية للوصول'}), 403
    flash('لا تملك صلاحية للوصول إلى هذه الصفحة', 'danger')
    return redirect(url_for('auth_login.login'))
