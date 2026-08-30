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
        # ✅ اختبار بسيط - تأكد من أن الصفحة تظهر
        return """
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>بوابة الموردين - محجوب أونلاين</title>
            <style>
                body { font-family: Arial, sans-serif; background: #05020a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
                .card { background: #0f071c; border: 1px solid #ce9e49; border-radius: 16px; padding: 40px; max-width: 400px; width: 100%; box-shadow: 0 8px 30px rgba(0,0,0,0.5); }
                .gold { color: #ce9e49; }
                h1 { text-align: center; font-size: 24px; }
                .input-group { margin-bottom: 16px; }
                label { display: block; margin-bottom: 6px; color: #ce9e49; font-size: 14px; }
                input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid rgba(206,158,73,0.3); background: rgba(15,7,28,0.8); color: #fff; font-size: 14px; }
                input:focus { border-color: #ce9e49; outline: none; }
                .btn { width: 100%; padding: 14px; background: linear-gradient(135deg, #ce9e49, #ba8b38); color: #05020a; border: none; border-radius: 8px; font-weight: bold; font-size: 16px; cursor: pointer; }
                .btn:hover { background: linear-gradient(135deg, #fae19c, #ce9e49); }
                .error { color: #fca5a5; background: rgba(220,38,38,0.15); padding: 12px; border-radius: 8px; margin-bottom: 16px; display: none; }
                .success { color: #86efac; background: rgba(34,197,94,0.15); padding: 12px; border-radius: 8px; margin-bottom: 16px; display: none; }
                .links { text-align: center; margin-top: 16px; font-size: 14px; }
                .links a { color: #ce9e49; text-decoration: none; }
                .links a:hover { text-decoration: underline; }
                .badge { display: inline-block; background: rgba(206,158,73,0.2); color: #fae19c; padding: 2px 10px; border-radius: 20px; font-size: 10px; border: 1px solid rgba(206,158,73,0.3); }
            </style>
        </head>
        <body>
            <div class="card">
                <div style="text-align:center; margin-bottom:24px;">
                    <div style="font-size:48px;">🛒</div>
                    <h1>محجوب أونلاين <span class="badge">سوقك الذكي</span></h1>
                    <p style="color:#ce9e49; font-size:14px;">بوابة الموردين وموظفيهم</p>
                </div>
                
                <div id="alertBox" class="error"></div>
                
                <form id="loginForm">
                    <div class="input-group">
                        <label>رقم الهاتف أو البريد الإلكتروني</label>
                        <input type="text" id="identifier" placeholder="مثال: 77xxxxxxx أو البريد" value="test_supplier">
                    </div>
                    <div class="input-group">
                        <label>كلمة المرور</label>
                        <input type="password" id="password" placeholder="••••••••" value="123">
                    </div>
                    <button type="submit" class="btn">دخول المنظومة</button>
                </form>
                
                <div class="links">
                    <a href="/suppliers/register">اشتراك مورد جديد</a> |
                    <a href="/suppliers/forgot-password">نسيت كلمة المرور؟</a>
                </div>
                
                <div style="margin-top:20px; padding-top:16px; border-top:1px solid rgba(206,158,73,0.15); text-align:center; font-size:12px; color:#666;">
                    ✅ البوابة تعمل بشكل صحيح
                </div>
            </div>
            
            <script>
                document.getElementById('loginForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    const identifier = document.getElementById('identifier').value;
                    const password = document.getElementById('password').value;
                    const alertBox = document.getElementById('alertBox');
                    
                    alertBox.style.display = 'none';
                    
                    try {
                        const response = await fetch('/suppliers/login', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ identifier, password, user_type: 'supplier', remember_me: true })
                        });
                        const data = await response.json();
                        
                        if (data.success) {
                            alertBox.className = 'success';
                            alertBox.textContent = '✅ ' + data.message;
                            alertBox.style.display = 'block';
                            setTimeout(() => { window.location.href = data.redirect_url; }, 1000);
                        } else {
                            alertBox.className = 'error';
                            alertBox.textContent = '❌ ' + data.message;
                            alertBox.style.display = 'block';
                        }
                    } catch(err) {
                        alertBox.className = 'error';
                        alertBox.textContent = '❌ خطأ في الاتصال بالخادم';
                        alertBox.style.display = 'block';
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
