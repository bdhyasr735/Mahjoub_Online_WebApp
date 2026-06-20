# coding: utf-8
# 📂 apps/vendors/routes.py - المحرك الأساسي لمسارات بوابة الموردين

from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.otp_db import OTPVerification
from .vendor_auth_service import vendor_login_required

vendors_bp = Blueprint('vendors', __name__, template_folder='templates')

@vendors_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    """معالجة عملية تسجيل الدخول وتوليد/التحقق من رمز OTP"""
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        phone = data.get('phone')
        otp = data.get('otp')

        # 1. طلب إرسال رمز التحقق
        if email and phone and not otp:
            raw_otp = OTPVerification.generate_otp(email)
            # هنا يجب إضافة دالة إرسال الرمز (SMS/Email)
            print(f"DEBUG: OTP Code for {email} is {raw_otp}") 
            return jsonify({"status": "pending", "message": "تم إرسال رمز التأكيد إلى بريدك"})

        # 2. التحقق من رمز OTP المدخل
        if email and otp:
            if OTPVerification.verify_otp(email, otp):
                # ربط الجلسة بالمورد
                supplier = Supplier.query.filter_by(_owner_email=email).first()
                if supplier:
                    session['vendor_authenticated'] = True
                    session['vendor_email'] = email
                    session['supplier_id'] = supplier.id
                    return jsonify({"status": "success", "redirect": url_for('vendors.dashboard')})
                else:
                    return jsonify({"status": "error", "message": "المورد غير مسجل في النظام"}), 404
            else:
                return jsonify({"status": "error", "message": "رمز التحقق غير صحيح أو منتهي"}), 400
        
        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400
    
    return render_template('vendor/login.html')

@vendors_bp.route('/quick-login', methods=['POST'])
def quick_login():
    """دخول سريع (لأغراض التطوير والاختبار)"""
    # تفعيل الدخول لأول مورد في قاعدة البيانات كمحاكاة
    first_supplier = Supplier.query.first()
    if first_supplier:
        session['vendor_authenticated'] = True
        session['supplier_id'] = first_supplier.id
        return jsonify({"status": "success", "redirect": url_for('vendors.dashboard')})
    return jsonify({"status": "error", "message": "لا يوجد موردون مسجلون"}), 400

@vendors_bp.route('/dashboard')
@vendor_login_required
def dashboard():
    """لوحة التحكم - عرض البيانات الحقيقية من الجداول"""
    supplier = Supplier.query.get(session.get('supplier_id'))
    return render_template('vendor/dashboard.html', 
                           vendor=supplier, 
                           wallet=supplier.wallet if supplier else None)

@vendors_bp.route('/logout')
def logout():
    """تسجيل الخروج وإنهاء الجلسة بشكل آمن"""
    session.clear()
    return redirect(url_for('vendors.login_page'))
