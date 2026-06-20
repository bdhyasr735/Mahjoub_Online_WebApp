# coding: utf-8
# 📂 apps/vendors/routes.py - المحرك الأساسي لمسارات بوابة الموردين (نسخة نهائية)

from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.otp_db import OTPVerification
from .vendor_auth_service import vendor_login_required

# تعريف الـ Blueprint الخاص بالموردين
vendors_bp = Blueprint('vendors', __name__, template_folder='templates')

# --------------------------------------------------------------------------
# المسار: بوابة تسجيل الدخول
# --------------------------------------------------------------------------
@vendors_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    """معالجة عملية تسجيل الدخول وتوليد/التحقق من رمز OTP"""
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "بيانات فارغة"}), 400
            
        email = data.get('email')
        phone = data.get('phone')
        otp = data.get('otp')

        # الحالة 1: طلب إرسال رمز التحقق
        if email and phone and not otp:
            # التحقق من وجود المورد قبل إرسال الرمز (اختياري لزيادة الأمان)
            supplier = Supplier.query.filter_by(_owner_email=email).first()
            if not supplier:
                return jsonify({"status": "error", "message": "البريد الإلكتروني غير مسجل"}), 404
                
            raw_otp = OTPVerification.generate_otp(email)
            print(f"DEBUG: OTP Code for {email} is {raw_otp}") 
            return jsonify({"status": "pending", "message": "تم إرسال رمز التأكيد إلى بريدك"})

        # الحالة 2: التحقق من رمز OTP المدخل
        if email and otp:
            if OTPVerification.verify_otp(email, otp):
                # ربط الجلسة بالمورد بعد التحقق الناجح
                supplier = Supplier.query.filter_by(_owner_email=email).first()
                if supplier:
                    session['vendor_authenticated'] = True
                    session['vendor_email'] = email
                    session['supplier_id'] = supplier.id
                    return jsonify({"status": "success", "redirect": url_for('vendors.dashboard')})
                else:
                    return jsonify({"status": "error", "message": "المورد غير موجود في قاعدة البيانات"}), 404
            else:
                return jsonify({"status": "error", "message": "رمز التحقق غير صحيح أو منتهي"}), 400
        
        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400
    
    return render_template('vendor/login.html')

# --------------------------------------------------------------------------
# المسار: دخول سريع (لأغراض الاختبار والتطوير)
# --------------------------------------------------------------------------
@vendors_bp.route('/quick-login', methods=['POST'])
def quick_login():
    """دخول سريع لمحاكاة الوصول المباشر للموردين"""
    first_supplier = Supplier.query.first()
    if first_supplier:
        session['vendor_authenticated'] = True
        session['supplier_id'] = first_supplier.id
        session['vendor_email'] = first_supplier._owner_email
        return jsonify({"status": "success", "redirect": url_for('vendors.dashboard')})
    return jsonify({"status": "error", "message": "لا يوجد موردون مسجلون"}), 404

# --------------------------------------------------------------------------
# المسار: لوحة التحكم (محمية)
# --------------------------------------------------------------------------
@vendors_bp.route('/dashboard')
@vendor_login_required
def dashboard():
    """عرض بيانات المورد الحقيقية من قاعدة البيانات"""
    supplier = Supplier.query.get(session.get('supplier_id'))
    return render_template(
        'vendor/dashboard.html', 
        vendor=supplier, 
        wallet=supplier.wallet if supplier else None
    )

# --------------------------------------------------------------------------
# المسار: تسجيل الخروج
# --------------------------------------------------------------------------
@vendors_bp.route('/logout')
def logout():
    """إنهاء الجلسة وتوجيه المورد لصفحة الدخول"""
    session.clear()
    return redirect(url_for('vendors.login_page'))
