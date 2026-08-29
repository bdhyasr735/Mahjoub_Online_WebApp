"""
apps/suppliers_auth_portal/routes.py
مسارات بوابة مصادقة وإدارة الموردين والموظفين
"""

import hashlib
import hmac
import os
import secrets
import time
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, g
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet

# ==================== دوال التشفير ====================
class PasswordHasher:
    @staticmethod
    def set_password(password: str) -> str:
        salt = os.urandom(16).hex()
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations=100000
        )
        return f"pbkdf2_sha256$100000${salt}${key.hex()}"

    @staticmethod
    def check_password(password: str, hashed: str) -> bool:
        try:
            algorithm, iterations, salt, key = hashed.split('$')
            test_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                iterations=int(iterations)
            )
            return hmac.compare_digest(key, test_key.hex())
        except Exception:
            return False

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

# ==================== تسجيل الدخول ====================
@suppliers_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'text/html' in request.headers.get('Accept', ''):
            return render_template(
                'suppliers_auth_portal/login.html',
                csrf_token=session.get('csrf_token', secrets.token_hex(32))
            )
        return jsonify({
            "status": "success",
            "message": "مرحباً بك في بوابة تسجيل الدخول للموردين",
            "csrf_token": session.get('csrf_token', secrets.token_hex(32))
        })

    data = request.get_json() if request.is_json else request.form
    
    identifier = (data.get("identifier") or data.get("username") or data.get("email") or data.get("phone", "")).strip()
    password = data.get("password", "")
    user_type = data.get("user_type", "supplier")

    if not identifier or not password:
        return jsonify({"success": False, "message": "الرجاء إدخال البريد الإلكتروني أو رقم الجوال وكلمة المرور"}), 400

    if not validate_csrf_token(data.get("csrf_token")):
        return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403

    # ========== تسجيل دخول الموظف ==========
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
        
        return jsonify({"success": False, "message": "رقم الجوال أو البريد الإلكتروني أو كلمة المرور لموظف المورد غير صحيحة"}), 401

    # ========== تسجيل دخول المورد ==========
    supplier = Supplier.query.filter(
        (Supplier.username == identifier) |
        (Supplier.search_phone == str(identifier)[-9:])
    ).first()
    
    if supplier and PasswordHasher.check_password(password, supplier.password_hash):
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
        supplier.last_login = datetime.utcnow()
        db.session.commit()
        
        employees = SupplierStaff.query.filter_by(supplier_id=supplier.id).all()
        
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

    return jsonify({"success": False, "message": "رقم الجوال أو البريد الإلكتروني أو كلمة المرور غير صحيحة"}), 401

# ==================== عرض صفحة التسجيل ====================
@suppliers_auth_bp.route('/register-page', methods=['GET'])
def register_page():
    return render_template(
        'suppliers_auth_portal/register.html',
        csrf_token=session.get('csrf_token', secrets.token_hex(32))
    )

# ==================== تسجيل مورد جديد ====================
@suppliers_auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() if request.is_json else request.form
    
    if not validate_csrf_token(data.get("csrf_token")):
        return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403
    
    company_name = data.get("company_name", "").strip()
    email = data.get("email", "").strip().lower()
    phone = data.get("phone", "").strip()
    password = data.get("password", "")

    if not all([company_name, email, phone, password]):
        return jsonify({"success": False, "message": "جميع الحقول الإلزامية مطلوبة"}), 400

    # التحقق من عدم التكرار
    if Supplier.query.filter_by(username=email).first():
        return jsonify({"success": False, "message": "البريد الإلكتروني مسجل مسبقاً"}), 400
    
    if Supplier.query.filter_by(search_phone=str(phone)[-9:]).first():
        return jsonify({"success": False, "message": "رقم الهاتف مسجل مسبقاً"}), 400

    try:
        password_hash = PasswordHasher.set_password(password)
        
        supplier = Supplier(
            username=email,
            owner_name=data.get("owner_name", "المفوض الرسمي"),
            trade_name=company_name,
            store_name=company_name,
            status='active',
            rank='bronze',
            created_at=datetime.utcnow()
        )
        supplier.phone = phone
        supplier.password_hash = password_hash
        
        db.session.add(supplier)
        db.session.flush()

        # إنشاء المحفظة
        wallet_number = f"SA{secrets.randbelow(89)+10}990000{secrets.token_hex(6).upper()}"
        wallet = SupplierWallet(
            supplier_id=supplier.id,
            wallet_code=wallet_number,
            balance_sar=0.00,
            hold_balance=0.00,
            currency="SAR",
            status="active",
            created_at=datetime.utcnow()
        )
        db.session.add(wallet)
        
        # إضافة الموظفين
        for emp in data.get("employees", []):
            if emp.get("full_name") and emp.get("email"):
                staff = SupplierStaff(
                    supplier_id=supplier.id,
                    username=emp["email"].strip().lower(),
                    full_name=emp["full_name"],
                    email=emp["email"].strip().lower(),
                    phone=emp.get("phone", "").strip(),
                    role="sales",
                    status="active",
                    created_at=datetime.utcnow()
                )
                staff.set_password(emp.get("password", "Staff@2025"))
                db.session.add(staff)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "تم تسجيل المورد وإنشاء المحفظة المالية بنجاح",
            "redirect_url": "/suppliers/login"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"حدث خطأ أثناء التسجيل: {str(e)}"}), 400

# ==================== صفحة استعادة كلمة المرور ====================
@suppliers_auth_bp.route('/forgot-password-page', methods=['GET'])
def forgot_password_page():
    return render_template(
        'suppliers_auth_portal/forgot_password.html',
        csrf_token=session.get('csrf_token', secrets.token_hex(32))
    )

# ==================== طلب OTP ====================
@suppliers_auth_bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
    data = request.get_json() if request.is_json else request.form
    
    if not validate_csrf_token(data.get("csrf_token")):
        return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403
    
    identifier = data.get("identifier", "").strip()
    if not identifier:
        return jsonify({"success": False, "message": "يرجى إدخال البريد الإلكتروني أو رقم الجوال"}), 400
    
    supplier = Supplier.query.filter(
        (Supplier.username == identifier) |
        (Supplier.search_phone == str(identifier)[-9:])
    ).first()
    
    if not supplier:
        return jsonify({"success": False, "message": "لم يتم العثور على حساب مرتبط بالبيانات المدخلة"}), 404

    otp_code = f"{secrets.randbelow(900000) + 100000}"
    expiry = datetime.utcnow() + timedelta(seconds=300)

    session['otp_data'] = {
        'identifier': identifier,
        'otp_code': otp_code,
        'target_id': supplier.id,
        'target_type': 'supplier',
        'expiry': expiry.isoformat(),
        'attempts': 0
    }

    return jsonify({
        "success": True,
        "message": "تم إرسال رمز التحقق",
        "otp_sent": True,
        "data": {
            "masked_phone": supplier.phone[:4] + "****" + supplier.phone[-3:] if supplier.phone else identifier,
            "_dev_otp": otp_code
        }
    }), 200

# ==================== إعادة تعيين كلمة المرور ====================
@suppliers_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() if request.is_json else request.form
    
    if not validate_csrf_token(data.get("csrf_token")):
        return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403
    
    otp_data = session.get('otp_data')
    if not otp_data:
        return jsonify({"success": False, "message": "انتهت صلاحية طلب إعادة التعيين"}), 400

    otp_code = data.get("otp_code", "")
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if otp_data['otp_code'] != otp_code:
        return jsonify({"success": False, "message": "رمز التحقق غير صحيح"}), 400

    if new_password != confirm_password:
        return jsonify({"success": False, "message": "كلمتا المرور غير متطابقتين"}), 400

    if len(new_password) < 8:
        return jsonify({"success": False, "message": "يجب أن تتكون كلمة المرور من 8 خانات على الأقل"}), 400

    supplier = Supplier.query.get(otp_data['target_id'])
    if supplier:
        supplier.password_hash = PasswordHasher.set_password(new_password)
        db.session.commit()

    session.pop('otp_data', None)

    return jsonify({
        "success": True,
        "message": "تم تحديث كلمة المرور بنجاح",
        "redirect_url": "/suppliers/login"
    }), 200

# ==================== صفحة التحقق ====================
@suppliers_auth_bp.route('/verify-page', methods=['GET'])
def verify_page():
    return render_template(
        'suppliers_auth_portal/verify.html',
        csrf_token=session.get('csrf_token', secrets.token_hex(32))
    )

# ==================== التحقق من OTP ====================
@suppliers_auth_bp.route('/verify', methods=['POST'])
def verify_otp():
    data = request.get_json() if request.is_json else request.form
    
    if not validate_csrf_token(data.get("csrf_token")):
        return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403
    
    otp_code = data.get("otp_code", "").strip()
    
    otp_data = session.get('otp_data')
    if not otp_data:
        return jsonify({"success": False, "message": "انتهت صلاحية رمز التحقق"}), 400
    
    if otp_data['otp_code'] != otp_code:
        return jsonify({"success": False, "message": "رمز التحقق غير صحيح"}), 400
    
    supplier = Supplier.query.get(otp_data['target_id'])
    if supplier:
        supplier.status = 'verified'
        db.session.commit()
    
    session.pop('otp_data', None)
    
    return jsonify({
        "success": True,
        "message": "تم التحقق من الحساب بنجاح",
        "redirect_url": "/suppliers/login"
    }), 200

# ==================== إعادة إرسال OTP ====================
@suppliers_auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    data = request.get_json() if request.is_json else request.form
    
    if not validate_csrf_token(data.get("csrf_token")):
        return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403
    
    otp_data = session.get('otp_data')
    if not otp_data:
        return jsonify({"success": False, "message": "لا يوجد طلب نشط لإعادة التعيين"}), 400
    
    new_otp = f"{secrets.randbelow(900000) + 100000}"
    otp_data['otp_code'] = new_otp
    otp_data['expiry'] = (datetime.utcnow() + timedelta(seconds=300)).isoformat()
    session['otp_data'] = otp_data
    
    return jsonify({
        "success": True,
        "message": "تم إرسال رمز تحقق جديد",
        "data": {
            "_dev_otp": new_otp
        }
    }), 200

# ==================== تسجيل الخروج ====================
@suppliers_auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    if request.method == 'GET' or 'text/html' in request.headers.get('Accept', ''):
        return redirect(url_for('suppliers_auth_bp.login'))
    return jsonify({"success": True, "message": "تم تسجيل الخروج بنجاح"}), 200

# ==================== لوحة التحكم ====================
@suppliers_auth_bp.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('suppliers_auth_bp.login'))
    return jsonify({
        "message": "مرحباً بك في لوحة التحكم",
        "user_id": session.get('user_id'),
        "user_type": session.get('user_type')
    })
