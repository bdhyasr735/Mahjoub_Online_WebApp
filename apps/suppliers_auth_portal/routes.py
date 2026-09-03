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
    """تسجيل الدخول للموردين (يدعم JSON و Form)"""
    if current_user.is_authenticated:
        return redirect(url_for('suppliers_auth_bp.dashboard'))
    
    if request.method == 'POST':
        # ✅ استقبال البيانات من JSON أو Form
        data = request.get_json(silent=True) or request.form.to_dict()
        identifier = data.get('identifier') or data.get('username')
        password = data.get('password')
        
        # ✅ البحث الشامل: اسم المستخدم، البريد الإلكتروني، أو رقم الهاتف (آخر 9 أرقام)
        supplier = Supplier.query.filter(
            (Supplier.username == identifier) |
            (Supplier.email == identifier) |
            (Supplier.search_phone == identifier) |
            (Supplier.phone == identifier)
        ).first()
        
        if supplier and supplier.check_password(password):
            login_user(supplier)
            return jsonify({
                "success": True,
                "message": "تم تسجيل الدخول بنجاح",
                "redirect_url": url_for('suppliers_auth_bp.dashboard')
            })
        else:
            return jsonify({
                "success": False,
                "message": "اسم المستخدم أو كلمة المرور غير صحيحة!"
            }), 401
    
    return render_template('suppliers_auth_portal/login.html')


@suppliers_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """تسجيل الدخول للموردين"""
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form.to_dict()
        username = data.get('username')
        password = data.get('password')
        owner_name = data.get('owner_name')
        store_name = data.get('store_name')
        phone = data.get('phone')
        
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
            return jsonify({
                "success": True,
                "message": "تم تسجيلك بنجاح",
                "redirect_url": url_for('suppliers_auth_bp.login')
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": f"حدث خطأ: {str(e)}"
            }), 400
    
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
        (Supplier.email == identifier) | 
        (Supplier.search_phone == identifier)
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
        (Supplier.email == identifier) |
        (Supplier.search_phone == identifier)
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
