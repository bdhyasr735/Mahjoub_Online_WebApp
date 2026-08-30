# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_routes.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from datetime import datetime
import secrets

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet

# ✅ إنشاء البلوبرنت - الاسم يجب أن يكون 'suppliers_auth'
bp = Blueprint('suppliers_auth', __name__)


# ============================================================
# 🟣 تسجيل الدخول
# ============================================================

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/suppliers/dashboard')
    
    if request.method == 'GET':
        # ✅ صفحة HTML مبسطة للاختبار
        return """
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>تسجيل الدخول - محجوب أونلاين</title>
            <style>
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #05020a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
                .card { background: #0f071c; border: 1px solid #ce9e49; border-radius: 20px; padding: 40px; max-width: 420px; width: 100%; box-shadow: 0 20px 60px rgba(0,0,0,0.8); }
                .logo { text-align: center; margin-bottom: 30px; }
                .logo h1 { font-size: 26px; background: linear-gradient(135deg, #ce9e49, #fae19c, #ce9e49); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
                .logo span { display: inline-block; background: rgba(206,158,73,0.2); color: #fae19c; padding: 2px 12px; border-radius: 20px; font-size: 10px; border: 1px solid rgba(206,158,73,0.3); }
                .logo p { color: #ce9e49; font-size: 14px; margin-top: 5px; }
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
            </style>
        </head>
        <body>
            <div class="card">
                <div class="logo">
                    <div style="font-size:48px;">🛒</div>
                    <h1>محجوب أونلاين <span>سوقك الذكي</span></h1>
                    <p>بوابة الموردين وموظفيهم</p>
                </div>
                <div id="alertBox" class="alert"></div>
                <form id="loginForm">
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
                document.getElementById('loginForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    const identifier = document.getElementById('identifier').value.trim();
                    const password = document.getElementById('password').value;
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
                            body: JSON.stringify({ identifier, password, user_type: 'supplier', remember_me: true })
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
        
        # استخراج آخر 9 أرقام من الهاتف
        digits = ''.join(filter(str.isdigit, identifier))
        search_phone = digits[-9:] if len(digits) >= 9 else None
        
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
            'redirect_url': '/suppliers/dashboard',
            'user': {'id': user.id, 'username': user.username, 'user_type': user_type, 'status': user.status}
        })
        
    except Exception as e:
        current_app.logger.error(f'❌ خطأ في تسجيل الدخول: {str(e)}')
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ في الخادم'}), 500


# ============================================================
# 🟣 تسجيل الخروج
# ============================================================

@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    username = current_user.username
    logout_user()
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect('/suppliers/login')


# ============================================================
# 🟣 التسجيل - صفحة HTML مبسطة
# ============================================================

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/suppliers/dashboard')
    
    if request.method == 'GET':
        return """
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تسجيل مورد جديد - محجوب أونلاين</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #05020a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
            .card { background: #0f071c; border: 1px solid #ce9e49; border-radius: 20px; padding: 40px; max-width: 500px; width: 100%; box-shadow: 0 20px 60px rgba(0,0,0,0.8); }
            .logo { text-align: center; margin-bottom: 30px; }
            .logo h1 { font-size: 26px; background: linear-gradient(135deg, #ce9e49, #fae19c, #ce9e49); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .logo span { display: inline-block; background: rgba(206,158,73,0.2); color: #fae19c; padding: 2px 12px; border-radius: 20px; font-size: 10px; border: 1px solid rgba(206,158,73,0.3); }
            .logo p { color: #ce9e49; font-size: 14px; margin-top: 5px; }
            .input-group { margin-bottom: 16px; }
            label { display: block; margin-bottom: 6px; color: #ce9e49; font-size: 13px; font-weight: 600; }
            input, select { width: 100%; padding: 12px 16px; border-radius: 12px; border: 1px solid rgba(206,158,73,0.25); background: rgba(15,7,28,0.9); color: #fff; font-size: 14px; transition: all 0.3s; }
            input:focus, select:focus { border-color: #ce9e49; outline: none; box-shadow: 0 0 20px rgba(206,158,73,0.15); }
            input::placeholder { color: rgba(255,255,255,0.3); }
            select option { background: #0f071c; }
            .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
            .btn { width: 100%; padding: 16px; background: linear-gradient(135deg, #ce9e49, #ba8b38); color: #05020a; border: none; border-radius: 12px; font-weight: 700; font-size: 16px; cursor: pointer; transition: all 0.3s; margin-top: 8px; }
            .btn:hover { background: linear-gradient(135deg, #fae19c, #ce9e49); box-shadow: 0 0 30px rgba(206,158,73,0.3); }
            .btn:disabled { opacity: 0.6; cursor: not-allowed; }
            .alert { padding: 12px 16px; border-radius: 10px; margin-bottom: 16px; display: none; font-size: 14px; }
            .alert-error { background: rgba(220,38,38,0.15); border: 1px solid rgba(220,38,38,0.3); color: #fca5a5; }
            .alert-success { background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.3); color: #86efac; }
            .links { text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(206,158,73,0.1); font-size: 13px; }
            .links a { color: #ce9e49; text-decoration: none; }
            .links a:hover { text-decoration: underline; }
            .footer { text-align: center; margin-top: 16px; font-size: 11px; color: #444; }
            .checkbox-group { display: flex; align-items: flex-start; gap: 10px; margin: 12px 0; }
            .checkbox-group input { width: 18px; height: 18px; margin-top: 2px; accent-color: #ce9e49; }
            .checkbox-group label { font-size: 12px; color: #94a3b8; cursor: pointer; }
            .checkbox-group label strong { color: #ce9e49; }
            .spinner { display: inline-block; width: 16px; height: 16px; border: 2px solid #05020a; border-top-color: transparent; border-radius: 50%; animation: spin 0.6s linear infinite; vertical-align: middle; margin-right: 8px; }
            @keyframes spin { to { transform: rotate(360deg); } }
        </style>
        </head>
        <body>
        <div class="card">
            <div class="logo"><div style="font-size:48px;">📝</div><h1>فتح حساب <span>مورد جديد</span></h1><p>انضم إلى منصة محجوب أونلاين</p></div>
            <div id="alertBox" class="alert"></div>
            <form id="registerForm">
                <div class="grid-2">
                    <div class="input-group"><label>اسم المنشأة *</label><input type="text" id="trade_name" placeholder="شركة النور للتجارة" required></div>
                    <div class="input-group"><label>اسم المالك *</label><input type="text" id="owner_name" placeholder="الاسم الثلاثي" required></div>
                </div>
                <div class="grid-2">
                    <div class="input-group"><label>رقم الهاتف *</label><input type="tel" id="phone" placeholder="77xxxxxxx" required></div>
                    <div class="input-group"><label>البريد الإلكتروني</label><input type="email" id="email" placeholder="supplier@domain.com"></div>
                </div>
                <div class="grid-2">
                    <div class="input-group"><label>اسم المستخدم *</label><input type="text" id="username" placeholder="اختر اسم مستخدم" required></div>
                    <div class="input-group"><label>اسم المتجر</label><input type="text" id="store_name" placeholder="اسم المتجر للعرض"></div>
                </div>
                <div class="grid-2">
                    <div class="input-group"><label>كلمة المرور *</label><input type="password" id="password" placeholder="•••••••• (8 أحرف)" required minlength="8"></div>
                    <div class="input-group"><label>تأكيد كلمة المرور *</label><input type="password" id="confirm_password" placeholder="••••••••" required minlength="8"></div>
                </div>
                <div class="input-group"><label>فئة النشاط *</label>
                    <select id="category" required>
                        <option value="">اختر فئة التوريد...</option>
                        <option value="food">المواد الغذائية</option>
                        <option value="electronics">الأجهزة الإلكترونية</option>
                        <option value="clothing">الملابس والمنسوجات</option>
                        <option value="wholesale">تجارة الجملة</option>
                        <option value="other">أخرى</option>
                    </select>
                </div>
                <div class="checkbox-group">
                    <input type="checkbox" id="agree_pricing_policy" required>
                    <label for="agree_pricing_policy">أوافق على التزام <strong>سعر التكلفة</strong> وأقر بحق المنصة في إيقاف الحساب في حال مخالفة ذلك.</label>
                </div>
                <button type="submit" class="btn" id="submitBtn">إرسال طلب التسجيل</button>
            </form>
            <div class="links"><a href="/suppliers/login">← تسجيل الدخول</a></div>
            <div class="footer">🔒 مشفر 256-bit SSL</div>
        </div>
        <script>
        document.getElementById('registerForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const alertBox = document.getElementById('alertBox');
            const submitBtn = document.getElementById('submitBtn');
            alertBox.style.display = 'none';
            alertBox.className = 'alert';
            
            const password = document.getElementById('password').value;
            const confirm = document.getElementById('confirm_password').value;
            if (password !== confirm) {
                alertBox.textContent = '⚠️ كلمتا المرور غير متطابقتين';
                alertBox.className = 'alert alert-error';
                alertBox.style.display = 'block';
                return;
            }
            if (password.length < 8) {
                alertBox.textContent = '⚠️ كلمة المرور يجب أن تكون 8 أحرف على الأقل';
                alertBox.className = 'alert alert-error';
                alertBox.style.display = 'block';
                return;
            }
            const phone = document.getElementById('phone').value.replace(/\D/g, '');
            if (phone.length < 9) {
                alertBox.textContent = '⚠️ رقم الهاتف يجب أن يحتوي على 9 أرقام';
                alertBox.className = 'alert alert-error';
                alertBox.style.display = 'block';
                return;
            }
            if (!document.getElementById('agree_pricing_policy').checked) {
                alertBox.textContent = '⚠️ يجب الموافقة على شروط حوكمة الأسعار';
                alertBox.className = 'alert alert-error';
                alertBox.style.display = 'block';
                return;
            }
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> جاري المعالجة...';
            
            try {
                const data = {
                    trade_name: document.getElementById('trade_name').value.trim(),
                    owner_name: document.getElementById('owner_name').value.trim(),
                    username: document.getElementById('username').value.trim(),
                    phone: document.getElementById('phone').value.trim(),
                    email: document.getElementById('email').value.trim(),
                    store_name: document.getElementById('store_name').value.trim(),
                    password: password,
                    category: document.getElementById('category').value,
                    agree_pricing_policy: document.getElementById('agree_pricing_policy').checked
                };
                
                const response = await fetch('/suppliers/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                
                if (result.success) {
                    alertBox.textContent = '✅ ' + result.message;
                    alertBox.className = 'alert alert-success';
                    alertBox.style.display = 'block';
                    setTimeout(() => { window.location.href = result.redirect_url; }, 1500);
                } else {
                    alertBox.textContent = '❌ ' + result.message;
                    alertBox.className = 'alert alert-error';
                    alertBox.style.display = 'block';
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'إرسال طلب التسجيل';
                }
            } catch(err) {
                alertBox.textContent = '❌ خطأ في الاتصال بالخادم';
                alertBox.className = 'alert alert-error';
                alertBox.style.display = 'block';
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'إرسال طلب التسجيل';
            }
        });
        </script>
        </body>
        </html>
        """
    
    # POST: معالجة التسجيل
    try:
        data = request.get_json() or request.form
        
        trade_name = data.get('trade_name', '').strip()
        owner_name = data.get('owner_name', '').strip()
        username = data.get('username', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip() or None
        store_name = data.get('store_name', '').strip() or trade_name
        password = data.get('password', '')
        agree = data.get('agree_pricing_policy', False)
        
        if not all([trade_name, owner_name, username, phone, password]):
            return jsonify({'success': False, 'message': 'يرجى ملء جميع الحقول المطلوبة'}), 400
        
        if not agree:
            return jsonify({'success': False, 'message': 'يجب الموافقة على شروط حوكمة الأسعار'}), 400
        
        if Supplier.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'اسم المستخدم موجود مسبقاً'}), 400
        
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 9:
            return jsonify({'success': False, 'message': 'رقم الهاتف يجب أن يحتوي على 9 أرقام'}), 400
        
        search_phone = digits[-9:]
        if Supplier.query.filter_by(search_phone=search_phone).first():
            return jsonify({'success': False, 'message': 'رقم الهاتف مسجل مسبقاً'}), 400
        
        if email and Supplier.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'البريد الإلكتروني مسجل مسبقاً'}), 400
        
        supplier = Supplier(
            username=username,
            email=email,
            owner_name=owner_name,
            trade_name=trade_name,
            store_name=store_name,
            status='pending'
        )
        supplier.phone = phone
        supplier.set_password(password)
        
        db.session.add(supplier)
        db.session.flush()
        
        wallet = SupplierWallet(
            supplier_id=supplier.id,
            wallet_code=f"WEL-963{supplier.id}",
            balance=0.0,
            status='active'
        )
        db.session.add(wallet)
        
        otp_code = generate_otp()
        session['verify_supplier_id'] = supplier.id
        session['verify_otp'] = otp_code
        
        db.session.commit()
        
        login_user(supplier)
        
        return jsonify({
            'success': True,
            'message': 'تم التسجيل بنجاح',
            'redirect_url': '/suppliers/verify',
            'data': {'_dev_otp': otp_code}
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'خطأ في التسجيل: {str(e)}')
        return jsonify({'success': False, 'message': 'حدث خطأ في الخادم'}), 500


# ============================================================
# 🟣 استعادة كلمة المرور
# ============================================================

@bp.route('/forgot-password', methods=['GET'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect('/suppliers/dashboard')
    
    return """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>استعادة كلمة المرور - محجوب أونلاين</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #05020a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .card { background: #0f071c; border: 1px solid #ce9e49; border-radius: 20px; padding: 40px; max-width: 420px; width: 100%; box-shadow: 0 20px 60px rgba(0,0,0,0.8); }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 { font-size: 26px; background: linear-gradient(135deg, #ce9e49, #fae19c, #ce9e49); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .logo p { color: #ce9e49; font-size: 14px; margin-top: 5px; }
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
        .links a { color: #ce9e49; text-decoration: none; }
        .links a:hover { text-decoration: underline; }
        .footer { text-align: center; margin-top: 16px; font-size: 11px; color: #444; }
        .spinner { display: inline-block; width: 16px; height: 16px; border: 2px solid #05020a; border-top-color: transparent; border-radius: 50%; animation: spin 0.6s linear infinite; vertical-align: middle; margin-right: 8px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .hidden { display: none; }
        .otp-container { display: flex; gap: 8px; justify-content: center; margin: 12px 0; }
        .otp-container input { width: 50px; height: 56px; text-align: center; font-size: 24px; font-weight: 700; }
    </style>
    </head>
    <body>
    <div class="card">
        <div class="logo"><div style="font-size:48px;">🔑</div><h1>استعادة <span>كلمة المرور</span></h1><p>أدخل بياناتك لإرسال رمز التحقق</p></div>
        <div id="alertBox" class="alert"></div>
        
        <!-- المرحلة 1: طلب OTP -->
        <div id="stage1">
            <form id="requestOtpForm">
                <div class="input-group">
                    <label>اسم المستخدم أو رقم الهاتف أو البريد</label>
                    <input type="text" id="identifier" placeholder="مثال: test_supplier" required>
                </div>
                <button type="submit" class="btn" id="btnRequestOtp">إرسال رمز التحقق</button>
            </form>
        </div>
        
        <!-- المرحلة 2: إعادة تعيين كلمة المرور -->
        <div id="stage2" class="hidden">
            <p style="font-size:13px; color:#94a3b8; text-align:center; margin-bottom:12px;">تم إرسال الرمز إلى: <strong id="maskedTarget" style="color:#ce9e49;"></strong></p>
            <form id="resetPasswordForm">
                <div class="input-group">
                    <label>رمز التحقق (6 أرقام)</label>
                    <div class="otp-container">
                        <input type="text" maxlength="1" class="otp-digit" inputmode="numeric" pattern="[0-9]">
                        <input type="text" maxlength="1" class="otp-digit" inputmode="numeric" pattern="[0-9]">
                        <input type="text" maxlength="1" class="otp-digit" inputmode="numeric" pattern="[0-9]">
                        <input type="text" maxlength="1" class="otp-digit" inputmode="numeric" pattern="[0-9]">
                        <input type="text" maxlength="1" class="otp-digit" inputmode="numeric" pattern="[0-9]">
                        <input type="text" maxlength="1" class="otp-digit" inputmode="numeric" pattern="[0-9]">
                    </div>
                    <input type="hidden" id="otpCode" name="otp_code">
                </div>
                <div class="input-group">
                    <label>كلمة المرور الجديدة</label>
                    <input type="password" id="newPassword" placeholder="•••••••• (8 أحرف)" minlength="8" required>
                </div>
                <div class="input-group">
                    <label>تأكيد كلمة المرور</label>
                    <input type="password" id="confirmPassword" placeholder="••••••••" minlength="8" required>
                </div>
                <button type="submit" class="btn" id="btnReset">تحديث كلمة المرور</button>
            </form>
        </div>
        
        <div class="links"><a href="/suppliers/login">← العودة لتسجيل الدخول</a></div>
        <div class="footer">🔒 مشفر 256-bit SSL</div>
    </div>
    <script>
        let activeIdentifier
