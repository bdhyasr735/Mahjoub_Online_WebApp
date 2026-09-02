# -*- coding: utf-8 -*-
# 📂 apps/supplier_service/routes.py
"""
مسارات بوابة الموردين - محجوب أونلاين
Supplier Portal Web & API Routes
"""

from flask import Blueprint, request, jsonify, render_template_string, render_template, redirect, url_for, session
from apps.supplier_service.service import SupplierService
from apps.models.supplier_db import Supplier

supplier_service_bp = Blueprint(
    'supplier_portal',
    __name__,
    template_folder='templates',
    url_prefix='/supplier'
)

# توافق مسار الاستدعاء القديم
supplier_bp = supplier_service_bp

supplier_service = SupplierService()

@supplier_service_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول للمورد"""
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form.to_dict() or {}
        phone = data.get('phone', '').strip()
        password = data.get('password', '').strip()
        
        if not phone or not password:
            return jsonify({"success": False, "error": "رقم الهاتف وكلمة المرور مطلوبة"}), 400

        supplier = Supplier.query.filter_by(phone=phone.replace("+", "").strip()).first()
        if not supplier or supplier.password != password:
            return jsonify({"success": False, "error": "بيانات الدخول غير صحيحة"}), 401

        session['supplier_id'] = supplier.id
        session['supplier_phone'] = supplier.phone
        return jsonify({
            "success": True, 
            "message": "تم تسجيل الدخول بنجاح", 
            "redirect_url": url_for('supplier_portal.dashboard')
        }), 200

    # تجربة كافة مسارات القوالب المحتملة لمنع TemplateNotFound تماماً
    for template_path in ['supplier/login.html', 'login.html', 'suppliers_auth_portal/login.html', 'supplier_login.html']:
        try:
            return render_template(template_path)
        except Exception:
            continue
            
    # قالب افتراضي طارئ يمنع تعطل السيرفر كلياً في حال عدم وجود أي ملف قالب نهائياً
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>تسجيل دخول الموردين - محجوب أونلاين</title>
        <style>
            body { font-family: Tahoma, sans-serif; background: #1a0b2e; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .login-box { background: #2d1254; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3); width: 350px; border: 1px solid #D4AF37; }
            h2 { text-align: center; color: #D4AF37; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input { width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #ccc; background: #fff; color: #000; box-sizing: border-box; }
            button { width: 100%; padding: 10px; background: #D4AF37; border: none; border-radius: 5px; color: #1a0b2e; font-weight: bold; cursor: pointer; font-size: 16px; }
            button:hover { background: #e5c158; }
            .error-msg { color: #ff6b6b; text-align: center; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>بوابة الموردين</h2>
            <form id="loginForm">
                <div class="form-group">
                    <label>رقم الهاتف:</label>
                    <input type="text" id="phone" required placeholder="أدخل رقم الهاتف">
                </div>
                <div class="form-group">
                    <label>كلمة المرور:</label>
                    <input type="password" id="password" required placeholder="أدخل كلمة المرور">
                </div>
                <button type="submit">دخول</button>
                <div id="errorMsg" class="error-msg"></div>
            </form>
        </div>
        <script>
            document.getElementById('loginForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const phone = document.getElementById('phone').value;
                const password = document.getElementById('password').value;
                const errorMsg = document.getElementById('errorMsg');
                
                try {
                    const response = await fetch('/supplier/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ phone, password })
                    });
                    const data = await response.json();
                    if (data.success) {
                        window.location.href = data.redirect_url;
                    } else {
                        errorMsg.textContent = data.error || 'حدث خطأ أثناء تسجيل الدخول';
                    }
                } catch (err) {
                    errorMsg.textContent = 'تعطل الاتصال بالخادم';
                }
            });
        </script>
    </body>
    </html>
    """)

@supplier_service_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """التحقق من رمز الـ OTP لإتمام العمليات (تسجيل/استعادة)"""
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    phone = data.get('phone', '').strip()
    otp_code = data.get('otp_code', '').strip()
    purpose = data.get('purpose', 'login')

    if not phone or not otp_code:
        return jsonify({"success": False, "error": "رقم الهاتف ورمز التحقق مطلوبان"}), 400

    result = supplier_service.verify_otp_code(phone, otp_code, purpose=purpose)
    if result.get("success"):
        supplier = result.get("supplier")
        if purpose == "login":
            session['supplier_id'] = supplier.id
            session['supplier_phone'] = supplier.phone
            return jsonify({
                "success": True, 
                "message": "تم التحقق وتسجيل الدخول بنجاح", 
                "redirect_url": url_for('supplier_portal.dashboard')
            }), 200
        return jsonify({"success": True, "message": "تم التحقق بنجاح"}), 200

    return jsonify(result), 400

@supplier_service_bp.route('/reset-password', methods=['POST'])
def reset_password_submit():
    """استقبال الكود الجديد وكلمة المرور الجديدة لإتمام الاستعادة"""
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    phone = data.get('phone', '').strip()
    otp_code = data.get('otp_code', '').strip()
    new_password = data.get('new_password', '').strip()

    if not phone or not otp_code or not new_password:
        return jsonify({"success": False, "error": "جميع الحقول مطلوبة"}), 400

    result = supplier_service.reset_supplier_password(phone, otp_code, new_password)
    if result.get("success"):
        return jsonify(result), 200

    return jsonify(result), 400

@supplier_service_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """لوحة تحكم المورد المحمية بجلسة العمل"""
    supplier_id = session.get('supplier_id')
    if not supplier_id:
        return redirect(url_for('supplier_portal.login'))
        
    supplier = supplier_service.get_supplier_profile(supplier_id)
    if not supplier:
        session.clear()
        return redirect(url_for('supplier_portal.login'))

    for template_path in ['dashboard.html', 'supplier/dashboard.html', 'suppliers_auth_portal/dashboard.html', 'supplier_dashboard.html']:
        try:
            return render_template(template_path, supplier=supplier)
        except Exception:
            continue

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="UTF-8"><title>لوحة تحكم المورد</title></head>
    <body style="background:#1a0b2e; color:#D4AF37; font-family:Tahoma; text-align:center; padding-top:50px;">
        <h1>مرحباً بك في لوحة تحكم المورد (محجوب أونلاين)</h1>
        <p>رقم الهاتف: {{ supplier.phone }}</p>
        <a href="/supplier/logout" style="color:#fff; background:#D4AF37; padding:10px 20px; text-decoration:none; border-radius:5px;">تسجيل الخروج</a>
    </body>
    </html>
    """, supplier=supplier)

@supplier_service_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """تسجيل خروج المورد وإنهاء الجلسة"""
    session.clear()
    return redirect(url_for('supplier_portal.login'))
