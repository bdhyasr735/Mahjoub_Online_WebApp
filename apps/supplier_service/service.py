# -*- coding: utf-8 -*-
# 📂 apps/supplier_service/routes.py
"""
مسارات بوابة الموردين - محجوب أونلاين
Supplier Portal Web & API Routes
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
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

    # البحث عن القالب مباشرة بالأسماء المتاحة دون فرض هيكل مجلد فرعي
    try:
        return render_template('login.html')
    except Exception:
        return render_template('suppliers_auth_portal/login.html')

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

    try:
        return render_template('dashboard.html', supplier=supplier)
    except Exception:
        return render_template('suppliers_auth_portal/dashboard.html', supplier=supplier)

@supplier_service_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """تسجيل خروج المورد وإنهاء الجلسة"""
    session.clear()
    return redirect(url_for('supplier_portal.login'))
