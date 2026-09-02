# -*- coding: utf-8 -*-
# 📂 apps/supplier_service/routes.py
"""
مسارات بوابة الموردين - محجوب أونلاين
Supplier Portal Web & API Routes
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from apps.supplier_service.service import SupplierService
from apps.models.supplier_db import Supplier, db

supplier_bp = Blueprint(
    'supplier_portal',
    __name__,
    template_folder='templates',
    url_prefix='/supplier'
)

supplier_service = SupplierService()

@supplier_bp.route('/login', methods=['GET', 'POST'])
def login():
    """تسجيل دخول المورد عبر رقم الهاتف وإرسال الـ OTP"""
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form.to_dict() or {}
        phone = data.get('phone', '').strip()
        
        if not phone:
            return jsonify({"error": "رقم الهاتف مطلوب"}), 400

        # توليد وإرسال الرمز
        supplier = Supplier.query.filter_by(phone=phone.replace("+", "").strip()).first()
        if not supplier:
            return jsonify({"error": "رقم الهاتف غير مسجل كمورد"}), 404

        result = supplier_service.generate_otp(supplier.id)
        if result.get("success"):
            return jsonify({"success": True, "message": "تم إرسال كود التحقق إلى واتساب", "supplier_id": supplier.id}), 200
        return jsonify({"error": result.get("error")}), 400

    return render_template('supplier/login.html')

@supplier_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """التحقق من الكود وإتمام تسجيل الدخول"""
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    phone = data.get('phone', '')
    otp_code = data.get('otp_code', '')

    result = supplier_service.verify_otp(phone, otp_code)
    if result.get("success"):
        supplier = result.get("supplier")
        session['supplier_id'] = supplier.id
        session['supplier_phone'] = supplier.phone
        return jsonify({"success": True, "redirect_url": url_for('supplier_portal.dashboard')}), 200

    return jsonify({"error": result.get("error")}), 400

@supplier_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """طلب استعادة كلمة المرور"""
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    phone = data.get('phone', '')
    
    result = supplier_service.request_password_reset(phone)
    if result.get("success"):
        return jsonify(result), 200
    return jsonify(result), 400

@supplier_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """لوحة تحكم المورد"""
    supplier_id = session.get('supplier_id')
    if not supplier_id:
        return redirect(url_for('supplier_portal.login'))
        
    supplier = Supplier.query.get(supplier_id)
    return render_template('supplier/dashboard.html', supplier=supplier)
