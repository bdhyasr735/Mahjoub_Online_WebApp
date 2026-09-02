# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/routes.py
"""
سوق محجوب أونلاين - مسارات مصادقة الموردين وبوابة رموز التحقق (OTP)
Flask / Python Routes for Supplier Authentication & OTP Service
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from apps.suppliers_auth_portal.otp_service import SupplierOTPService
from apps.models.supplier_db import Supplier

# تصحيح بادئة المسار لتتطابق مع /supplier بدلاً من /suppliers لتجنب أخطاء 404
suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    template_folder='templates',
    url_prefix='/supplier'
)


@suppliers_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل دخول الموردين عبر رقم الهاتف أو معرف الاتصال"""
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form.to_dict() or {}
        identifier = data.get('identifier', '').strip()
        
        if not identifier:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": False, "error": "يرجى إدخال رقم الهاتف أو المعرف"}), 400
            flash('يرجى إدخال رقم الهاتف أو المعرف', 'danger')
            return render_template('suppliers_auth_portal/login.html')
            
        # التحقق من وجود المورد في قاعدة البيانات
        clean_id = identifier.replace("+", "").strip()
        supplier = Supplier.query.filter(
            (Supplier.phone == clean_id) | (Supplier.phone == identifier)
        ).first()
        
        if not supplier:
            error_msg = "رقم الهاتف غير مسجل كتاجر أو مورد معتمد في منصة محجوب أونلاين"
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": False, "error": error_msg}), 404
            flash(error_msg, 'danger')
            return render_template('suppliers_auth_portal/login.html')
            
        # توليد وإرسال رمز التحقق (OTP) عبر خدمة الواتساب
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        result = SupplierOTPService.generate_and_send_otp(
            identifier=clean_id,
            target_id=supplier.id,
            target_type='supplier',
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if not result.get("success"):
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(result), 500
            flash(result.get("error", "فشل إرسال رمز التحقق"), 'danger')
            return render_template('suppliers_auth_portal/login.html')
            
        # تخزين المعرف مؤقتاً في الجلسة للانتقال لخطوة التحقق من الرمز
        session['otp_identifier'] = clean_id
        session['otp_supplier_id'] = supplier.id
        
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": True,
                "message": "تم إرسال رمز التحقق بنجاح إلى هاتفك عبر الواتساب",
                "redirect_url": url_for('suppliers_auth_bp.supplier_verify')
            }), 200
            
        return redirect(url_for('suppliers_auth_bp.supplier_verify'))

    return render_template('suppliers_auth_portal/login.html')


@suppliers_auth_bp.route('/verify', methods=['GET', 'POST'])
def supplier_verify():
    """صفحة إدخال والتحقق من رمز الـ OTP المرسل للمورد"""
    identifier = session.get('otp_identifier')
    supplier_id = session.get('otp_supplier_id')
    
    if not identifier:
        flash('انتهت صلاحية الجلسة أو لم تقم بإدخال رقم الهاتف', 'warning')
        return redirect(url_for('suppliers_auth_bp.login'))
        
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form.to_dict() or {}
        entered_otp = data.get('otp_code') or data.get('code', '').strip()
        
        if not entered_otp:
            error_msg = "يرجى إدخال رمز التحقق المكون من الأرقام المرسلة"
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": False, "error": error_msg}), 400
            flash(error_msg, 'danger')
            return render_template('suppliers_auth_portal/verify.html', identifier=identifier)
            
        # التحقق من صحة الرمز باستخدام خدمة OTP
        verification_res = SupplierOTPService.verify_otp(identifier, entered_otp)
        
        if not verification_res.get("success"):
            error_msg = verification_res.get("error", "رمز التحقق غير صحيح أو انتهت صلاحيته")
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": False, "error": error_msg}), 400
            flash(error_msg, 'danger')
            return render_template('suppliers_auth_portal/verify.html', identifier=identifier)
            
        # تسجيل الدخول بنجاح وتثبيت الجلسة للمورد
        session['supplier_logged_in'] = True
        session['supplier_id'] = supplier_id
        session['supplier_phone'] = identifier
        
        # تنظيف جلسة الـ OTP المؤقتة
        session.pop('otp_identifier', None)
        session.pop('otp_supplier_id', None)
        
        success_msg = "تم تسجيل الدخول بنجاح إلى لوحة الموردين"
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": True,
                "message": success_msg,
                "redirect_url": url_for('suppliers_auth_bp.supplier_dashboard')
            }), 200
            
        flash(success_msg, 'success')
        return redirect(url_for('suppliers_auth_bp.supplier_dashboard'))

    return render_template('suppliers_auth_portal/verify.html', identifier=identifier)


@suppliers_auth_bp.route('/dashboard', methods=['GET'])
def supplier_dashboard():
    """لوحة تحكم المورد الرئيسية بعد تسجيل الدخول الناجح"""
    if not session.get('supplier_logged_in') or not session.get('supplier_id'):
        flash('يرجى تسجيل الدخول أولاً للوصول إلى لوحة الموردين', 'warning')
        return redirect(url_for('suppliers_auth_bp.login'))
        
    supplier_id = session.get('supplier_id')
    supplier = Supplier.query.get(supplier_id)
    
    if not supplier:
        session.clear()
        return redirect(url_for('suppliers_auth_bp.login'))
        
    return render_template('suppliers_auth_portal/dashboard.html', supplier=supplier)


@suppliers_auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password_page():
    """صفحة استعادة كلمة المرور للموردين"""
    if request.method == 'POST':
        # منطق طلب استعادة كلمة المرور
        flash('تم إرسال تعليمات الاستعادة إلى وسائل الاتصال الخاصة بك إن كانت مسجلة.', 'info')
        return redirect(url_for('suppliers_auth_bp.login'))
    return render_template('suppliers_auth_portal/forgot_password.html')


@suppliers_auth_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    """صفحة تسجيل وانضمام مورد جديد للمنصة"""
    if request.method == 'POST':
        # منطق تسجيل المورد الجديد
        pass
    return render_template('suppliers_auth_portal/register.html')


@suppliers_auth_bp.route('/logout', methods=['POST', 'GET'])
def supplier_logout():
    """إنهاء جلسة المورد وتسجيل الخروج"""
    session.pop('supplier_logged_in', None)
    session.pop('supplier_id', None)
    session.pop('supplier_phone', None)
    
    flash('تم تسجيل الخروج بنجاح من بوابة الموردين', 'info')
    return redirect(url_for('suppliers_auth_bp.login'))


def init_app(app):
    """دالة تهيئة وتسجيل الـ Blueprint مع التطبيق الرئيسي"""
    app.register_blueprint(suppliers_auth_bp)
