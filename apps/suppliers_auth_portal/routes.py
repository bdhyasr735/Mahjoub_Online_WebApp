# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from apps.models.supplier_db import Supplier
from apps.extensions import db
from apps.suppliers_auth_portal.otp_service import SupplierOTPService

# ⚠️ هذا هو الاسم الذي يجب أن يكون موجوداً
suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    template_folder='templates',
    url_prefix='/supplier'
)


@suppliers_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """تسجيل الدخول للموردين"""
    if current_user.is_authenticated:
        return redirect(url_for('suppliers_auth_bp.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            supplier = Supplier.query.filter_by(username=username).first()
            if supplier and supplier.check_password(password):
                login_user(supplier)
                return redirect(url_for('suppliers_auth_bp.dashboard'))
            else:
                flash('اسم المستخدم أو كلمة المرور غير صحيحة!', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    return render_template('suppliers_auth_portal/login.html')


@suppliers_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """تسجيل الدخول للموردين"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        owner_name = request.form.get('owner_name')
        store_name = request.form.get('store_name')
        phone = request.form.get('phone')
        
        try:
            supplier = Supplier(
                username=username,
                password=password,
                owner_name=owner_name,
                store_name=store_name,
                phone=phone
            )
            db.session.add(supplier)
            db.session.commit()
            flash('تم تسجيلك بنجاح!', 'success')
            return redirect(url_for('suppliers_auth_bp.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    return render_template('suppliers_auth_portal/register.html')


@suppliers_auth_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """لوحة تحكم الموردين"""
    return render_template('suppliers_auth_portal/dashboard.html')


@suppliers_auth_bp.route('/forgot-password', methods=['GET'])
def forgot_password():
    """عرض صفحة استعادة كلمة المرور"""
    return render_template('suppliers_auth_portal/forgot_password.html')


@suppliers_auth_bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """طلب إرسال رمز التحقق OTP"""
    data = request.get_json()
    identifier = data.get('identifier', '')
    
    # البحث عن المورد
    supplier = Supplier.query.filter(
        (Supplier.phone == identifier) | 
        (Supplier.username == identifier) | 
        (Supplier.email == identifier)
    ).first()
    
    if not supplier:
        return jsonify({"success": False, "message": "لم يتم العثور على حساب مرتبط بالبيانات المدخلة."}), 404
    
    # إرسال OTP
    result = SupplierOTPService.generate_and_send_otp(
        identifier=supplier.phone,
        target_id=supplier.id,
        target_type='supplier'
    )
    
    if result.get('success'):
        return jsonify({
            "success": True,
            "message": "تم إرسال رمز التحقق بنجاح.",
            "data": {
                "masked_phone": f"****{supplier.phone[-4:]}",
                "_dev_otp": result.get('otp_code')
            }
        })
    
    return jsonify({"success": False, "message": "فشل إرسال رمز التحقق."}), 500


@suppliers_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """إعادة تعيين كلمة المرور باستخدام OTP"""
    data = request.get_json()
    identifier = data.get('identifier', '')
    otp_code = data.get('otp_code', '')
    new_password = data.get('new_password', '')
    
    # التحقق من OTP
    verification = SupplierOTPService.verify_otp(identifier, otp_code)
    
    if not verification.get('success'):
        return jsonify({"success": False, "message": "رمز التحقق غير صحيح أو انتهت صلاحيته."}), 400
    
    # تحديث كلمة المرور
    supplier = Supplier.query.filter(
        (Supplier.phone == identifier) | 
        (Supplier.username == identifier) | 
        (Supplier.email == identifier)
    ).first()
    
    if not supplier:
        return jsonify({"success": False, "message": "لم يتم العثور على الحساب."}), 404
    
    supplier.password = new_password
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "تم تحديث كلمة المرور بنجاح.",
        "redirect_url": url_for('suppliers_auth_bp.login')
    })


@suppliers_auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('suppliers_auth_bp.login'))
