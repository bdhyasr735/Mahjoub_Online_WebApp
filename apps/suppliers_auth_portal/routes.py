# -*- coding: utf-8 -*-
# apps/suppliers_auth_portal/routes.py

from flask import render_template, request, jsonify, session, redirect, url_for
from flask_login import login_user, current_user
from apps.suppliers_auth_portal import suppliers_auth_bp
from apps.suppliers_auth_portal.seo_service import SupplierPortalSEOService
from apps.suppliers_auth_portal.registry import SupplierPortalRegistry
from apps.suppliers_auth_portal.security import (
    validate_phone_number, validate_email, 
    check_rate_limit, record_failed_attempt, clear_rate_limit
)
from apps.models.supplier_db import Supplier
from apps.extensions import db

@suppliers_auth_bp.route('/login', methods=['GET'])
def login_page():
    seo = SupplierPortalSEOService.get_meta_tags("login")
    return render_template('suppliers_auth_portal/login.html', seo=seo)

@suppliers_auth_bp.route('/login', methods=['POST'])
def login():
    try:
        ip = request.remote_addr
        allowed, wait_time = check_rate_limit(ip)
        if not allowed:
            return jsonify({
                "success": False,
                "message": f"تم حظر المحاولات مؤقتاً بسبب تجاوز الحد المسموح. يرجى الانتظار {wait_time} ثانية."
            }), 429

        data = request.get_json(force=True, silent=True) or request.form or {}
        identifier = data.get('identifier', '').strip()
        password = data.get('password', '')
        user_type = data.get('user_type', 'supplier')

        if not identifier or not password:
            return jsonify({"success": False, "message": "يرجى إدخال اسم المستخدم/الهاتف وكلمة المرور."}), 400

        # استخراج آخر 9 أرقام للبحث في حقل search_phone لتفادي خطأ التشفير
        clean_phone_suffix = identifier[-9:] if identifier.isdigit() else identifier

        supplier_obj = Supplier.query.filter(
            (Supplier.username == identifier) | 
            (Supplier.email == identifier) |
            (Supplier.search_phone == clean_phone_suffix)
        ).first()

        # التحقق من وجود الحساب ووجود كلمة مرور مشفرة وتطابقها
        if supplier_obj and supplier_obj.password_hash and supplier_obj.check_password(password):
            clear_rate_limit(ip)
            session['user_type'] = 'supplier'
            login_user(supplier_obj)
            session['supplier_logged_in'] = True
            session['supplier_identifier'] = identifier
            return jsonify({
                "success": True,
                "message": "تم تسجيل الدخول بنجاح",
                # توجيه المورد مباشرة إلى لوحة التحكم (Dashboard) بعد تسجيل الدخول بنجاح
                "redirect_url": url_for('suppliers_auth_bp.dashboard')
            })
        else:
            record_failed_attempt(ip)
            return jsonify({"success": False, "message": "بيانات الاعتماد غير صحيحة. يرجى التحقق."}), 401
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500

@suppliers_auth_bp.route('/register', methods=['GET'])
def register_page():
    seo = SupplierPortalSEOService.get_meta_tags("register")
    return render_template('suppliers_auth_portal/register.html', seo=seo)

@suppliers_auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json(force=True, silent=True) or request.form or {}
        
        required_fields = ['company_name', 'full_address', 'owner_name', 'email', 'phone', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "message": f"يرجى استكمال الحقل الإلزامي: {field}"}), 400

        if not validate_email(data.get('email')):
            return jsonify({"success": False, "message": "صيغة البريد الإلكتروني غير صالحة."}), 400

        if not validate_phone_number(data.get('phone')):
            return jsonify({"success": False, "message": "صيغة رقم الجوال غير صحيحة."}), 400

        success, result = SupplierPortalRegistry.register_new_supplier(data)
        
        if success:
            session['pending_verification_phone'] = data.get('phone')
            return jsonify({
                "success": True,
                "message": "تم إنشاء طلب التسجيل والمحفظة المالية بنجاح.",
                "data": result,
                "redirect_url": url_for('suppliers_auth_bp.verify_page')
            })
        else:
            error_msg = result.get("error") if isinstance(result, dict) else "حدث خطأ أثناء حفظ بيانات المنشأة."
            return jsonify({"success": False, "message": error_msg}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500

@suppliers_auth_bp.route('/verify', methods=['GET'])
def verify_page():
    seo = SupplierPortalSEOService.get_meta_tags("verify")
    return render_template('suppliers_auth_portal/verify.html', seo=seo)

@suppliers_auth_bp.route('/verify', methods=['POST'])
def verify():
    try:
        data = request.get_json(force=True, silent=True) or request.form or {}
        otp_code = data.get('otp_code', '').strip()
        
        # جلب المعرف أو رقم الهاتف المخزن مؤقتاً في الجلسة للتحقق الفعلي من قاعدة البيانات
        identifier = session.get('pending_verification_phone') or session.get('supplier_identifier')

        success, message = SupplierPortalRegistry.verify_supplier_otp(identifier, otp_code)
        if success:
            session['supplier_verified'] = True
            return jsonify({
                "success": True,
                "message": message,
                # توجيه المورد إلى لوحة التحكم (Dashboard) مباشرةً بعد إتمام التحقق بنجاح
                "redirect_url": url_for('suppliers_auth_bp.dashboard')
            })
        else:
            return jsonify({"success": False, "message": message}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500

@suppliers_auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    return jsonify({
        "success": True,
        "message": "تم إرسال رمز تحقق جديد بنجاح إلى هاتفك المسجل."
    })

@suppliers_auth_bp.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    seo = SupplierPortalSEOService.get_meta_tags("forgot_password")  # ✅ تم التصحيح
    return render_template('suppliers_auth_portal/forgot_password.html', seo=seo)

@suppliers_auth_bp.route('/forgot-password/request-otp', methods=['POST'])
def forgot_password_request_otp():
    try:
        data = request.get_json(force=True, silent=True) or request.form or {}
        identifier = data.get('identifier', '').strip()
        
        if not identifier:
            return jsonify({"success": False, "message": "يرجى إدخال اسم المستخدم أو رقم الهاتف أو البريد الإلكتروني."}), 400

        mock_otp = "123456"
        session['reset_identifier'] = identifier
        
        return jsonify({
            "success": True,
            "otp_sent": True,
            "message": "تم إرسال رمز التحقق بنجاح.",
            "data": {
                "masked_phone": identifier[:3] + "****" + identifier[-2:] if len(identifier) > 5 else "77***89",
                "_dev_otp": mock_otp
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500

@suppliers_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json(force=True, silent=True) or request.form or {}
        otp_code = data.get('otp_code', '').strip()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')

        if otp_code != "123456":
            return jsonify({"success": False, "message": "رمز التحقق غير صحيح."}), 400

        if not new_password or new_password != confirm_password:
            return jsonify({"success": False, "message": "كلمتا المرور غير متطابقتين أو غير صالحتين."}), 400

        identifier = session.get('reset_identifier')
        if not identifier:
            return jsonify({"success": False, "message": "انتهت صلاحية الجلسة، يرجى إعادة محاولة استعادة كلمة المرور."}), 400

        clean_phone_suffix = identifier[-9:] if identifier.isdigit() else identifier
        supplier_obj = Supplier.query.filter(
            (Supplier.username == identifier) | 
            (Supplier.email == identifier) |
            (Supplier.search_phone == clean_phone_suffix) |
            (Supplier.phone == identifier)
        ).first()

        if not supplier_obj:
            return jsonify({"success": False, "message": "المورد غير موجود."}), 404

        # تحديث كلمة المرور الفعليّة في قاعدة البيانات وتشفيرها
        supplier_obj.set_password(new_password)
        db.session.commit()
        session.pop('reset_identifier', None)

        return jsonify({
            "success": True,
            "message": "تم تحديث كلمة المرور بنجاح",
            "redirect_url": url_for('suppliers_auth_bp.login_page')
        })
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500

@suppliers_auth_bp.route('/dashboard', methods=['GET'])
def dashboard():
    if not current_user.is_authenticated or session.get('user_type') != 'supplier':
        return redirect(url_for('suppliers_auth_bp.login_page'))
    return "<h1>لوحة تحكم الموردين الملكية - قيد العرض والتطوير</h1>"
