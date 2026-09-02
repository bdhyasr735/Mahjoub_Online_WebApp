# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/routes.py
"""
مسارات المصادقة والتسجيل وإدارة لوحة تحكم الموردين - محجوب أونلاين
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from apps.extensions import db
from apps.models.suppliers_db import Supplier  # نموذج جدول الموردين المصحح
from apps.models.wallet import SupplierWallet  # نموذج محفظة المورد المالية
from apps.suppliers_auth_portal.otp_service import SupplierOTPService

suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp', 
    __name__, 
    template_folder='templates',
    static_folder='static'
)

@suppliers_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """مسار تسجيل دخول الموردين برقم الهاتف وكلمة المرور أو التحقق الثنائي"""
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = request.get_json() or {}
        phone = data.get('phone', '').strip().replace("+", "")
        password = data.get('password', '')

        if not phone or not password:
            return jsonify({"success": False, "message": "الرجاء إدخال رقم الهاتف وكلمة المرور."}), 400

        # البحث عن المورد برقم الهاتف
        supplier = Supplier.query.filter_by(phone=phone).first()
        if not supplier or not check_password_hash(supplier.password_hash, password):
            return jsonify({"success": False, "message": "رقم الهاتف أو كلمة المرور غير صحيحة."}), 401

        # التحقق مما إذا كان الحساب موقوفاً بسبب ميثاق حوكمة الأسعار
        if getattr(supplier, 'is_suspended', False):
            return jsonify({"success": False, "message": "تم توقيف لوحة التحكم نظراً لمخالفة ميثاق حوكمة الأسعار والتكلفة."}), 403

        # تسجيل الدخول عبر Flask-Login
        login_user(supplier, remember=True)
        session['supplier_id'] = supplier.id
        session['supplier_phone'] = supplier.phone

        return jsonify({
            "success": True, 
            "message": "تم تسجيل الدخول بنجاح. جاري تحويلك إلى لوحة التحكم...", 
            "redirect_url": url_for('suppliers_auth_bp.dashboard')
        })

    if request.method == 'POST':
        phone = request.form.get('phone', '').strip().replace("+", "")
        password = request.form.get('password', '')

        supplier = Supplier.query.filter_by(phone=phone).first()
        if supplier and check_password_hash(supplier.password_hash, password):
            if getattr(supplier, 'is_suspended', False):
                flash('تم توقيف لوحة التحكم نظراً لمخالفة ميثاق حوكمة الأسعار والتكلفة.', 'danger')
                return redirect(url_for('suppliers_auth_bp.login'))

            login_user(supplier, remember=True)
            session['supplier_id'] = supplier.id
            session['supplier_phone'] = supplier.phone
            flash('تم تسجيل الدخول بنجاح.', 'success')
            return redirect(url_for('suppliers_auth_bp.dashboard'))
        else:
            flash('رقم الهاتف أو كلمة المرور غير صحيحة.', 'danger')

    return render_template('suppliers_auth_portal/login.html')


@suppliers_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """مسار تسجيل مورد جديد برقم الهاتف وإنشاء المحفظة المالية الذكية تلقائياً"""
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = request.get_json() or {}
        phone = data.get('phone', '').strip().replace("+", "")
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')

        if not phone or len(phone) != 9:
            return jsonify({"success": False, "message": "رقم الهاتف يجب أن يتكون من 9 أرقام صحيحة."}), 400

        if not password or len(password) < 8:
            return jsonify({"success": False, "message": "كلمة المرور يجب أن تكون 8 أحرف على الأقل."}), 400

        if password != confirm_password:
            return jsonify({"success": False, "message": "كلمتا المرور غير متطابقتين."}), 400

        # التأكد من عدم مسبقية تسجيل رقم الهاتف
        existing_supplier = Supplier.query.filter_by(phone=phone).first()
        if existing_supplier:
            return jsonify({"success": False, "message": "رقم الهاتف مسجل مسبقاً، يمكنك تسجيل الدخول مباشرة."}), 400

        try:
            # 1. إنشاء سجل المورد الجديد وتشفير كلمة المرور
            hashed_password = generate_password_hash(password)
            new_supplier = Supplier(
                phone=phone,
                password_hash=hashed_password,
                is_active=True
            )
            db.session.add(new_supplier)
            db.session.flushforkeys if hasattr(db.session, 'flushforkeys') else db.session.flush()

            # 2. إنشاء وتفعيل المحفظة المالية الذكية التلقائية (SupplierWallet)
            new_wallet = SupplierWallet(
                supplier_id=new_supplier.id,
                balance=0.00,
                currency="YER",
                is_active=True
            )
            db.session.add(new_wallet)
            db.session.commit()

            # 3. إرسال إشعار ترحبي أو رمز تحقق عبر الواتساب اختياري إن أمكن
            client_ip = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            SupplierOTPService.generate_and_send_otp(
                identifier=phone, 
                target_id=new_supplier.id, 
                target_type='supplier', 
                ip_address=client_ip, 
                user_agent=user_agent
            )

            return jsonify({
                "success": True,
                "message": "تم إنشاء الحساب والمحفظة المالية الذكية بنجاح!",
                "redirect_url": url_for('suppliers_auth_bp.login')
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"حدث خطأ داخلي أثناء عملية التسجيل: {str(e)}"}), 500

    return render_template('suppliers_auth_portal/register.html')


@suppliers_auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """مسار استعادة كلمة المرور عبر رقم الهاتف ورمز التحقق OTP"""
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip().replace("+", "")
        supplier = Supplier.query.filter_by(phone=phone).first()
        
        if not supplier:
            flash('رقم الهاتف غير مسجل في النظام.', 'danger')
            return redirect(url_for('suppliers_auth_bp.forgot_password'))

        # توليد وإرسال رمز التحقق عبر الواتساب
        otp_res = SupplierOTPService.generate_and_send_otp(
            identifier=phone,
            target_id=supplier.id,
            target_type='supplier_password_reset',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        if otp_res.get("success"):
            session['reset_phone'] = phone
            flash('تم إرسال رمز التحقق (OTP) إلى رقم واتساب الخاص بك بنجاح.', 'success')
            return redirect(url_for('suppliers_auth_bp.verify_reset_otp'))
        else:
            flash(otp_res.get("error", "فشل إرسال رمز التحقق."), 'danger')

    return render_template('suppliers_auth_portal/forgot_password.html')


@suppliers_auth_bp.route('/verify-reset-otp', methods=['GET', 'POST'])
def verify_reset_otp():
    """التحقق من رمز الاستعادة وتحديث كلمة المرور"""
    phone = session.get('reset_phone')
    if not phone:
        return redirect(url_for('suppliers_auth_bp.forgot_password'))

    if request.method == 'POST':
        entered_code = request.form.get('otp_code', '').strip()
        new_password = request.form.get('new_password', '')

        verify_res = SupplierOTPService.verify_otp(phone, entered_code)
        if not verify_res.get("success"):
            flash(verify_res.get("message", "رمز التحقق غير صحيح أو منتهي الصلاحية."), 'danger')
            return render_template('suppliers_auth_portal/verify_reset_otp.html')

        if not new_password or len(new_password) < 8:
            flash('كلمة المرور الجديدة يجب ألا تقل عن 8 أحرف.', 'danger')
            return render_template('suppliers_auth_portal/verify_reset_otp.html')

        supplier = Supplier.query.filter_by(phone=phone).first()
        if supplier:
            supplier.password_hash = generate_password_hash(new_password)
            db.session.commit()
            session.pop('reset_phone', None)
            flash('تم تحديث كلمة المرور بنجاح، يمكنك تسجيل الدخول الآن.', 'success')
            return redirect(url_for('suppliers_auth_bp.login'))

    return render_template('suppliers_auth_portal/verify_reset_otp.html')


@suppliers_auth_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة تحكم المورد المحمية"""
    wallet = SupplierWallet.query.filter_by(supplier_id=current_user.id).first()
    return render_template('suppliers_auth_portal/dashboard.html', wallet=wallet)


@suppliers_auth_bp.route('/logout')
def logout():
    """تسجيل خروج المورد وتنظيف الجلسة"""
    logout_user()
    session.clear()
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('suppliers_auth_bp.login'))
