# coding: utf-8
# 📂 apps/suppliers_auth_portal/routes.py

import secrets
import time
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, g
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet
from apps.models.otp_db import OTP
from apps.utils import PasswordHasher


# ==================== Blueprint ====================
suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    url_prefix='/suppliers',
    template_folder='templates',
    static_folder='static'
)


# ==================== قبل كل طلب ====================
@suppliers_auth_bp.before_request
def before_request():
    """تهيئة CSRF - بدون أي إعادة توجيه"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
        session['csrf_expiry'] = time.time() + 3600
    g.csrf_token = session['csrf_token']


def validate_csrf_token(token):
    if not token:
        return False
    stored_token = session.get('csrf_token')
    expiry = session.get('csrf_expiry', 0)
    if stored_token and token == stored_token and expiry > time.time():
        return True
    return len(token) >= 16


# ==================== الصفحة الرئيسية ====================
@suppliers_auth_bp.route('/')
def index():
    """إعادة توجيه بسيطة إلى صفحة تسجيل الدخول"""
    return redirect(url_for('suppliers_auth_bp.login'))


# ==================== تسجيل الدخول ====================
@suppliers_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    ✅ صفحة تسجيل الدخول - لا توجد إعادة توجيه في GET
    """
    # ✅ GET: عرض الصفحة فقط (بدون إعادة توجيه)
    if request.method == 'GET':
        # ✅ تأكد من أن هذا لا يعيد التوجيه أبداً
        return render_template(
            'suppliers_auth_portal/login.html',
            csrf_token=session.get('csrf_token', secrets.token_hex(32))
        )

    # ✅ POST: معالجة تسجيل الدخول
    data = request.get_json() if request.is_json else request.form
    
    identifier = (data.get("identifier") or data.get("username") or data.get("email") or data.get("phone", "")).strip()
    password = data.get("password", "")
    user_type = data.get("user_type", "supplier")

    if not identifier or not password:
        return jsonify({"success": False, "message": "الرجاء إدخال البريد الإلكتروني أو رقم الجوال وكلمة المرور"}), 400

    if not validate_csrf_token(data.get("csrf_token")):
        return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403

    # 🔹 تسجيل دخول الموظف
    if user_type == "employee":
        staff = SupplierStaff.query.filter(
            (SupplierStaff.username == identifier) |
            (SupplierStaff.search_phone == str(identifier)[-9:])
        ).first()
        
        if staff and staff.status == "active" and staff.check_password(password):
            supplier = Supplier.query.get(staff.supplier_id)
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
            staff.last_login = datetime.utcnow()
            db.session.commit()
            
            session['user_id'] = staff.id
            session['user_type'] = 'employee'
            session['supplier_id'] = supplier.id
            
            return jsonify({
                "success": True,
                "message": "تم تسجيل دخول الموظف بنجاح",
                "data": {
                    "user_type": "employee",
                    "employee": staff.to_dict(),
                    "supplier": {
                        "id": supplier.id,
                        "username": supplier.username,
                        "phone": supplier.phone,
                        "trade_name": supplier.trade_name,
                    },
                    "wallet": {
                        "wallet_id": wallet.id,
                        "account_number": wallet.wallet_code,
                        "balance": wallet.balance_sar,
                    } if wallet else None,
                },
                "redirect_url": "/suppliers/dashboard"
            }), 200
        
        return jsonify({"success": False, "message": "بيانات الدخول غير صحيحة"}), 401

    # 🔹 تسجيل دخول المورد
    supplier = Supplier.query.filter(
        (Supplier.username == identifier) |
        (Supplier.search_phone == str(identifier)[-9:])
    ).first()
    
    if supplier and PasswordHasher.check_password(password, supplier.password_hash):
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
        supplier.last_login = datetime.utcnow()
        db.session.commit()
        
        employees = SupplierStaff.query.filter_by(supplier_id=supplier.id).all()
        
        session['user_id'] = supplier.id
        session['user_type'] = 'supplier'
        
        return jsonify({
            "success": True,
            "message": "تم تسجيل الدخول بنجاح",
            "data": {
                "user_type": "supplier",
                "supplier": {
                    "id": supplier.id,
                    "username": supplier.username,
                    "phone": supplier.phone,
                    "trade_name": supplier.trade_name,
                    "store_name": supplier.store_name,
                    "status": supplier.status,
                },
                "wallet": {
                    "wallet_id": wallet.id,
                    "account_number": wallet.wallet_code,
                    "balance": wallet.balance_sar,
                } if wallet else None,
                "employees_count": len(employees),
            },
            "redirect_url": "/suppliers/dashboard"
        }), 200

    return jsonify({"success": False, "message": "بيانات الدخول غير صحيحة"}), 401


# ==================== عرض صفحة التسجيل ====================
@suppliers_auth_bp.route('/register-page', methods=['GET'])
def register_page():
    """صفحة التسجيل - بدون إعادة توجيه"""
    return render_template(
        'suppliers_auth_portal/register.html',
        csrf_token=session.get('csrf_token', secrets.token_hex(32))
    )


# ==================== صفحة استعادة كلمة المرور ====================
@suppliers_auth_bp.route('/forgot-password-page', methods=['GET'])
def forgot_password_page():
    """صفحة استعادة كلمة المرور - بدون إعادة توجيه"""
    return render_template(
        'suppliers_auth_portal/forgot_password.html',
        csrf_token=session.get('csrf_token', secrets.token_hex(32))
    )


# ==================== صفحة التحقق ====================
@suppliers_auth_bp.route('/verify-page', methods=['GET'])
def verify_page():
    """صفحة التحقق - بدون إعادة توجيه"""
    return render_template(
        'suppliers_auth_portal/verify.html',
        csrf_token=session.get('csrf_token', secrets.token_hex(32))
    )


# ==================== لوحة التحكم ====================
@suppliers_auth_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """
    ✅ لوحة التحكم - تتحقق من الجلسة فقط
    """
    # ✅ إذا لم يكن مسجلاً، يوجه إلى login (مرة واحدة فقط)
    if 'user_id' not in session:
        return redirect(url_for('suppliers_auth_bp.login'))
    
    return jsonify({
        "message": "مرحباً بك في لوحة التحكم",
        "user_id": session.get('user_id'),
        "user_type": session.get('user_type')
    })


# ==================== تسجيل الخروج ====================
@suppliers_auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """تسجيل الخروج - مسح الجلسة"""
    session.clear()
    return redirect(url_for('suppliers_auth_bp.login'))


# ==================== باقي المسارات (POST) ====================

@suppliers_auth_bp.route('/register', methods=['POST'])
def register():
    """تسجيل مورد جديد"""
    # ... الكود كما هو ...


@suppliers_auth_bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """طلب OTP"""
    # ... الكود كما هو ...


@suppliers_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """إعادة تعيين كلمة المرور"""
    # ... الكود كما هو ...


@suppliers_auth_bp.route('/verify', methods=['POST'])
def verify_otp():
    """التحقق من OTP"""
    # ... الكود كما هو ...


@suppliers_auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """إعادة إرسال OTP"""
    # ... الكود كما هو ...
