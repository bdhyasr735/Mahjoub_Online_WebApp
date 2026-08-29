# coding: utf-8
# 📂 apps/suppliers_auth_portal/routes.py

print("=" * 60)
print("🚀 [DEBUG] routes.py is being loaded!")
print("=" * 60)

"""
🚪 مسارات بوابة المصادقة للموردين والموظفين
تسجيل الدخول، التسجيل، استعادة كلمة المرور، التحقق
"""

import secrets
import time
import traceback
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, g
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet
from apps.models.otp_db import OTP

# ✅ استيراد أدوات الأمان من نفس المجلد
from .security import PasswordHasher, CSRFProtector

print("✅ [DEBUG] All imports completed in routes.py")

# ==================== Blueprint ====================
suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    url_prefix='/suppliers',
    template_folder='templates',
    static_folder='static'
)

print(f"✅ [DEBUG] Blueprint created: {suppliers_auth_bp.name}")

# ==================== قبل كل طلب ====================
@suppliers_auth_bp.before_request
def before_request():
    """تهيئة CSRF - بدون إعادة توجيه"""
    print(f"🔍 [BEFORE_REQUEST] Path: {request.path}")
    print(f"🔍 [BEFORE_REQUEST] Session: {dict(session)}")
    
    if 'csrf_token' not in session:
        CSRFProtector.generate_token()
        print(f"🔍 [BEFORE_REQUEST] تم إنشاء CSRF Token جديد")
    
    g.csrf_token = session.get('csrf_token')
    print(f"🔍 [BEFORE_REQUEST] g.csrf_token: {g.csrf_token}")

def validate_csrf_token(token):
    """التحقق من CSRF"""
    return CSRFProtector.validate_token(token)

# ==================== الصفحة الرئيسية ====================
@suppliers_auth_bp.route('/')
def index():
    print(f"🔍 [INDEX] Redirecting to login")
    return redirect(url_for('suppliers_auth_bp.login'))

# ==================== مسار اختبار ====================
@suppliers_auth_bp.route('/test')
def test():
    print("🔍 [TEST] Test route called!")
    return jsonify({
        "status": "success",
        "message": "✅ البوابة تعمل!",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

# ==================== تسجيل الدخول ====================
@suppliers_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        print(f"🔍 [LOGIN] Called with method: {request.method}")
        print(f"🔍 [LOGIN] Session: {dict(session)}")
        print(f"🔍 [LOGIN] Headers Accept: {request.headers.get('Accept', '')}")
        
        if request.method == 'GET':
            print(f"🔍 [LOGIN] Rendering login.html")
            return render_template(
                'suppliers_auth_portal/login.html',
                csrf_token=CSRFProtector.get_token()
            )

        data = request.get_json() if request.is_json else request.form
        print(f"🔍 [LOGIN] POST data: {data}")
        
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
        
    except Exception as e:
        print(f"❌ [LOGIN] Exception: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

# ==================== عرض صفحة التسجيل ====================
@suppliers_auth_bp.route('/register-page', methods=['GET'])
def register_page():
    try:
        print(f"🔍 [REGISTER_PAGE] Rendering register.html")
        return render_template(
            'suppliers_auth_portal/register.html',
            csrf_token=CSRFProtector.get_token()
        )
    except Exception as e:
        print(f"❌ [REGISTER_PAGE] Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

# ==================== تسجيل مورد جديد ====================
@suppliers_auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json() if request.is_json else request.form
        
        if not validate_csrf_token(data.get("csrf_token")):
            return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403
        
        company_name = data.get("company_name", "").strip()
        email = data.get("email", "").strip().lower()
        phone = data.get("phone", "").strip()
        password = data.get("password", "")

        if not all([company_name, email, phone, password]):
            return jsonify({"success": False, "message": "جميع الحقول الإلزامية مطلوبة"}), 400

        if Supplier.query.filter_by(username=email).first():
            return jsonify({"success": False, "message": "البريد الإلكتروني مسجل مسبقاً"}), 400
        
        if Supplier.query.filter_by(search_phone=str(phone)[-9:]).first():
            return jsonify({"success": False, "message": "رقم الهاتف مسجل مسبقاً"}), 400

        password_hash = PasswordHasher.set_password(password)
        
        supplier = Supplier(
            username=email,
            email=email,
            owner_name=data.get("owner_name", "المفوض الرسمي"),
            trade_name=company_name,
            store_name=company_name,
            status='active',
            rank='bronze',
            created_at=datetime.utcnow()
        )
        supplier.phone = phone
        supplier.search_phone = str(phone)[-9:]
        supplier.password_hash = password_hash
        
        db.session.add(supplier)
        db.session.flush()

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
        
        for emp in data.get("employees", []):
            if emp.get("full_name") and emp.get("email"):
                staff = SupplierStaff(
                    supplier_id=supplier.id,
                    username=emp["email"].strip().lower(),
                    full_name=emp["full_name"],
                    email=emp["email"].strip().lower(),
                    phone=emp.get("phone", "").strip(),
                    role=emp.get("role", "sales"),
                    status="active",
                    created_at=datetime.utcnow()
                )
                if emp.get("phone"):
                    staff.search_phone = str(emp["phone"])[-9:]
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
        print(f"❌ [REGISTER] Error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"حدث خطأ أثناء التسجيل: {str(e)}"}), 400

# ==================== صفحة استعادة كلمة المرور ====================
@suppliers_auth_bp.route('/forgot-password-page', methods=['GET'])
def forgot_password_page():
    try:
        print(f"🔍 [FORGOT_PASSWORD_PAGE] Rendering forgot_password.html")
        return render_template(
            'suppliers_auth_portal/forgot_password.html',
            csrf_token=CSRFProtector.get_token()
        )
    except Exception as e:
        print(f"❌ [FORGOT_PASSWORD_PAGE] Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

# ==================== طلب OTP ====================
@suppliers_auth_bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
    try:
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

        otp, otp_code = OTP.create_otp(
            identifier=identifier,
            target_id=supplier.id,
            target_type='supplier',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return jsonify({
            "success": True,
            "message": "تم إرسال رمز التحقق",
            "otp_sent": True,
            "data": {
                "masked_phone": supplier.phone[:4] + "****" + supplier.phone[-3:] if supplier.phone else identifier,
                "_dev_otp": otp_code
            }
        }), 200
        
    except Exception as e:
        print(f"❌ [REQUEST_OTP] Error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"حدث خطأ: {str(e)}"}), 500

# ==================== إعادة تعيين كلمة المرور ====================
@suppliers_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json() if request.is_json else request.form
        
        if not validate_csrf_token(data.get("csrf_token")):
            return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403
        
        otp_code = data.get("otp_code", "")
        new_password = data.get("new_password", "")
        confirm_password = data.get("confirm_password", "")

        otp_record = OTP.get_valid_otp(otp_code)
        
        if not otp_record:
            return jsonify({"success": False, "message": "رمز التحقق غير صحيح أو منتهي الصلاحية"}), 400

        result = otp_record.verify(otp_code)
        if not result['success']:
            return jsonify({"success": False, "message": result['message']}), 400

        if new_password != confirm_password:
            return jsonify({"success": False, "message": "كلمتا المرور غير متطابقتين"}), 400

        if len(new_password) < 8:
            return jsonify({"success": False, "message": "يجب أن تتكون كلمة المرور من 8 خانات على الأقل"}), 400

        supplier = Supplier.query.get(otp_record.target_id)
        if supplier:
            supplier.password_hash = PasswordHasher.set_password(new_password)
            db.session.commit()

        return jsonify({
            "success": True,
            "message": "تم تحديث كلمة المرور بنجاح",
            "redirect_url": "/suppliers/login"
        }), 200
        
    except Exception as e:
        print(f"❌ [RESET_PASSWORD] Error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"حدث خطأ: {str(e)}"}), 500

# ==================== صفحة التحقق ====================
@suppliers_auth_bp.route('/verify-page', methods=['GET'])
def verify_page():
    try:
        print(f"🔍 [VERIFY_PAGE] Rendering verify.html")
        return render_template(
            'suppliers_auth_portal/verify.html',
            csrf_token=CSRFProtector.get_token()
        )
    except Exception as e:
        print(f"❌ [VERIFY_PAGE] Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

# ==================== التحقق من OTP ====================
@suppliers_auth_bp.route('/verify', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json() if request.is_json else request.form
        
        if not validate_csrf_token(data.get("csrf_token")):
            return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403
        
        otp_code = data.get("otp_code", "").strip()
        
        otp_record = OTP.get_valid_otp(otp_code)
        
        if not otp_record:
            return jsonify({"success": False, "message": "رمز التحقق غير صحيح أو منتهي الصلاحية"}), 400
        
        result = otp_record.verify(otp_code)
        if not result['success']:
            return jsonify({"success": False, "message": result['message']}), 400
        
        supplier = Supplier.query.get(otp_record.target_id)
        if supplier:
            supplier.status = 'verified'
            db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "تم التحقق من الحساب بنجاح",
            "redirect_url": "/suppliers/login"
        }), 200
        
    except Exception as e:
        print(f"❌ [VERIFY_OTP] Error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"حدث خطأ: {str(e)}"}), 500

# ==================== إعادة إرسال OTP ====================
@suppliers_auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    try:
        data = request.get_json() if request.is_json else request.form
        
        if not validate_csrf_token(data.get("csrf_token")):
            return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403
        
        identifier = data.get("identifier", "")
        
        if not identifier:
            return jsonify({"success": False, "message": "المعرف مطلوب"}), 400
        
        last_otp = OTP.query.filter_by(
            identifier=identifier,
            is_used=False
        ).first()
        
        if not last_otp:
            return jsonify({"success": False, "message": "لا يوجد طلب نشط لإعادة التعيين"}), 400
        
        otp, otp_code = OTP.create_otp(
            identifier=identifier,
            target_id=last_otp.target_id,
            target_type=last_otp.target_type,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        last_otp.is_used = True
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "تم إرسال رمز تحقق جديد",
            "data": {
                "_dev_otp": otp_code
            }
        }), 200
        
    except Exception as e:
        print(f"❌ [RESEND_OTP] Error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"حدث خطأ: {str(e)}"}), 500

# ==================== تسجيل الخروج ====================
@suppliers_auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    print(f"🔍 [LOGOUT] Clearing session")
    session.clear()
    return redirect(url_for('suppliers_auth_bp.login'))

# ==================== لوحة التحكم ====================
@suppliers_auth_bp.route('/dashboard', methods=['GET'])
def dashboard():
    try:
        print(f"🔍 [DASHBOARD] Session: {dict(session)}")
        if 'user_id' not in session:
            print(f"🔍 [DASHBOARD] No user_id, redirecting to login")
            return redirect(url_for('suppliers_auth_bp.login'))
        
        return jsonify({
            "message": "مرحباً بك في لوحة التحكم",
            "user_id": session.get('user_id'),
            "user_type": session.get('user_type')
        })
    except Exception as e:
        print(f"❌ [DASHBOARD] Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

# ==================== طباعة المسارات للتأكد ====================
print("=" * 60)
print("✅ [DEBUG] routes.py loaded successfully!")
print("📋 [DEBUG] Routes defined in this blueprint:")
for rule in suppliers_auth_bp.url_map.iter_rules():
    print(f"   📍 {rule}")
print("=" * 60)
