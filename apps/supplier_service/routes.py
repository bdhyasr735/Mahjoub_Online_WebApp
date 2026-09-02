# -*- coding: utf-8 -*-
# 📂 apps/supplier_service/routes.py
"""
مسارات بوابة الموردين - محجوب أونلاين
Supplier Portal Web & API Routes
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from apps.supplier_service.service import SupplierService
from apps.models.supplier_db import Supplier

supplier_bp = Blueprint(
    'supplier_portal',
    __name__,
    template_folder='templates',
    url_prefix='/supplier'
)

supplier_service = SupplierService()

@supplier_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول وإرسال رمز التحقق (OTP) للمورد"""
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form.to_dict() or {}
        phone = data.get('phone', '').strip()
        
        if not phone:
            return jsonify({"success": False, "error": "رقم الهاتف مطلوب"}), 400

        result = supplier_service.generate_and_send_otp(phone, purpose="login")
        if result.get("success"):
            return jsonify(result), 200
        return jsonify(result), 400

    return render_template('supplier/login.html')

@supplier_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """التحقق من رمز الـ OTP وإتمام تسجيل دخول المورد"""
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    phone = data.get('phone', '').strip()
    otp_code = data.get('otp_code', '').strip()

    if not phone or not otp_code:
        return jsonify({"success": False, "error": "رقم الهاتف ورمز التحقق مطلوبان"}), 400

    result = supplier_service.verify_otp_code(phone, otp_code, purpose="login")
    if result.get("success"):
        supplier = result.get("supplier")
        session['supplier_id'] = supplier.id
        session['supplier_phone'] = supplier.phone
        return jsonify({
            "success": True, 
            "message": "تم تسجيل الدخول بنجاح", 
            "redirect_url": url_for('supplier_portal.dashboard')
        }), 200

    return jsonify(result), 400

@supplier_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """طلب استعادة كلمة المرور وإرسال رمز إعادة التعيين عبر الواتساب"""
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    phone = data.get('phone', '').strip()
    
    if not phone:
        return jsonify({"success": False, "error": "رقم الهاتف مطلوب"}), 400

    result = supplier_service.generate_and_send_otp(phone, purpose="password_reset")
    if result.get("success"):
        return jsonify(result), 200
        
    return jsonify(result), 400

@supplier_bp.route('/reset-password', methods=['POST'])
def reset_password_submit():
    """استقبال الكود الجديد وكلمة المرور الجديدة لإتمام الاستعادة"""
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    phone = data.get('phone', '').strip()
    otp_code = data.get('otp_code', '').strip()
    new_password = data.get('new_password', '').strip()

    if not phone or not otp_code or not new_password:
        return jsonify({"success": False, "error": "جميع الحقول (الهاتف، الرمز، كلمة المرور الجديدة) مطلوبة"}), 400

    result = supplier_service.reset_supplier_password(phone, otp_code, new_password)
    if result.get("success"):
        return jsonify(result), 200

    return jsonify(result), 400

@supplier_bp.route('/register-request', methods=['POST'])
def register_request():
    """طلب اشتراك أو تفعيل حساب لمورد جديد عبر إرسال OTP"""
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    phone = data.get('phone', '').strip()
    
    if not phone:
        return jsonify({"success": False, "error": "رقم الهاتف مطلوب"}), 400

    result = supplier_service.generate_and_send_otp(phone, purpose="register")
    if result.get("success"):
        return jsonify(result), 200
    return jsonify(result), 400

@supplier_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """لوحة تحكم المورد المحمية بجلسة العمل"""
    supplier_id = session.get('supplier_id')
    if not supplier_id:
        return redirect(url_for('supplier_portal.login'))
        
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        session.clear()
        return redirect(url_for('supplier_portal.login'))

    return render_template('supplier/dashboard.html', supplier=supplier)

@supplier_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """تسجيل خروج المورد وإنهاء الجلسة"""
    session.clear()
    return redirect(url_for('supplier_portal.login'))
