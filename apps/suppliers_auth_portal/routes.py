# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/routes.py

from flask import render_template, request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user, current_user
from apps.suppliers_auth_portal import suppliers_bp
from apps.suppliers_auth_portal.seo_service import SupplierPortalSEOService
from apps.suppliers_auth_portal.security import (
    validate_phone_number, validate_email,
    check_rate_limit, record_failed_attempt, clear_rate_limit,
    SupplierAuthSecurity
)
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.extensions import db

# ✅ استيراد Registry
from apps.suppliers_auth_portal.registry import SupplierPortalRegistry


@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 🟢 معالجة طلب GET (عرض الصفحة)
    if request.method == 'GET':
        seo = SupplierPortalSEOService.get_meta_tags("login")
        return render_template('suppliers_auth_portal/login.html', seo=seo)

    # 🔴 معالجة طلب POST (تسجيل الدخول)
    try:
        ip = request.remote_addr
        allowed, wait_time = check_rate_limit(ip)
        if not allowed:
            return jsonify({
                "success": False,
                "message": f"تم حظر المحاولات مؤقتاً. يرجى الانتظار {wait_time} ثانية."
            }), 429

        data = request.get_json(force=True, silent=True) or request.form or {}
        identifier = data.get('identifier', '').strip()
        password = data.get('password', '')
        user_type = data.get('user_type', 'supplier')

        if not identifier or not password:
            return jsonify({"success": False, "message": "يرجى إدخال اسم المستخدم وكلمة المرور."}), 400

        clean_phone_suffix = identifier[-9:] if identifier.isdigit() else identifier

        if user_type == 'supplier':
            supplier_obj = db.session.query(Supplier).filter(
                (Supplier.username == identifier) |
                (Supplier.email == identifier) |
                (Supplier.search_phone == clean_phone_suffix)
            ).first()

            if not supplier_obj:
                return jsonify({"success": False, "message": "المورد غير مسجل"}), 404

            if not supplier_obj.check_password(password):
                return jsonify({"success": False, "message": "كلمة المرور غير صحيحة"}), 401

            clear_rate_limit(ip)
            session['user_type'] = 'supplier'
            login_user(supplier_obj)
            session['supplier_logged_in'] = True
            session['supplier_identifier'] = identifier
            
            return jsonify({
                "success": True,
                "message": "تم تسجيل الدخول بنجاح",
                "redirect_url": url_for('suppliers_dashboard.dashboard')
            })

        elif user_type == 'employee':
            staff_obj = db.session.query(SupplierStaff).filter(
                (SupplierStaff.username == identifier) |
                (SupplierStaff.email == identifier) |
                (SupplierStaff.search_phone == clean_phone_suffix)
            ).first()

            if not staff_obj:
                return jsonify({"success": False, "message": "موظف المورد غير مسجل"}), 404

            if not staff_obj.check_password(password):
                return jsonify({"success": False, "message": "كلمة المرور غير صحيحة"}), 401

            clear_rate_limit(ip)
            session['user_type'] = 'supplier_staff'
            login_user(staff_obj)
            session['supplier_staff_logged_in'] = True
            session['supplier_identifier'] = identifier
            
            return jsonify({
                "success": True,
                "message": "تم تسجيل الدخول بنجاح",
                "redirect_url": url_for('suppliers_dashboard.dashboard')
            })

        else:
            return jsonify({"success": False, "message": "نوع المستخدم غير صحيح"}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500


@suppliers_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('suppliers_bp.login'))


@suppliers_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        seo = SupplierPortalSEOService.get_meta_tags("register")
        return render_template('suppliers_auth_portal/register.html', seo=seo)

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
                "redirect_url": url_for('suppliers_bp.verify')
            })
        else:
            error_msg = result.get("error") if isinstance(result, dict) else "حدث خطأ أثناء حفظ بيانات المنشأة."
            return jsonify({"success": False, "message": error_msg}), 400
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500


@suppliers_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'GET':
        seo = SupplierPortalSEOService.get_meta_tags("verify")
        return render_template('suppliers_auth_portal/verify.html', seo=seo)

    try:
        data = request.get_json(force=True, silent=True) or request.form or {}
        otp_code = data.get('otp_code', '').strip()
        
        is_registration_flow = session.get('pending_verification_phone') is not None
        identifier = session.get('pending_verification_phone') or session.get('supplier_identifier')

        if not identifier:
            return jsonify({"success": False, "message": "انتهت صلاحية الجلسة، يرجى إعادة المحاولة."}), 400

        success, message = SupplierPortalRegistry.verify_supplier_otp(identifier, otp_code)
        if success:
            if is_registration_flow:
                session['supplier_verified'] = True
                session['user_type'] = 'supplier'
                
                clean_phone_suffix = identifier[-9:] if identifier and identifier.isdigit() else identifier
                supplier_obj = db.session.query(Supplier).filter(
                    (Supplier.phone == identifier) |
                    (Supplier.search_phone == clean_phone_suffix) |
                    (Supplier.email == identifier)
                ).first()

                if supplier_obj:
                    login_user(supplier_obj)
                    session['supplier_logged_in'] = True
                
                session.pop('pending_verification_phone', None)

            return jsonify({
                "success": True,
                "message": message,
                "redirect_url": url_for('suppliers_dashboard.dashboard')
            })
        else:
            return jsonify({"success": False, "message": message}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500


@suppliers_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    return jsonify({
        "success": True,
        "message": "تم إرسال رمز تحقق جديد بنجاح إلى هاتفك المسجل."
    })


@suppliers_bp.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    seo = SupplierPortalSEOService.get_meta_tags("forgot_password")
    return render_template('suppliers_auth_portal/forgot_password.html', seo=seo)


@suppliers_bp.route('/forgot-password/request-otp', methods=['POST'])
def forgot_password_request_otp():
    try:
        data = request.get_json(force=True, silent=True) or request.form or {}
        identifier = data.get('identifier', '').strip()
        
        if not identifier:
            return jsonify({"success": False, "message": "يرجى إدخال اسم المستخدم أو رقم الهاتف أو البريد الإلكتروني."}), 400

        clean_phone_suffix = identifier[-9:] if identifier.isdigit() else identifier
        supplier_obj = db.session.query(Supplier).filter(
            (Supplier.username == identifier) |
            (Supplier.email == identifier) |
            (Supplier.search_phone == clean_phone_suffix) |
            (Supplier.phone == identifier)
        ).first()

        if not supplier_obj:
            return jsonify({"success": False, "message": "المورد غير مسجل في النظام."}), 404

        # إرسال الرمز الحقيقي عبر وحدة الأمان (واتساب مع بديل البريد الإلكتروني)
        res = SupplierAuthSecurity.generate_and_send_otp(supplier_obj, channel='whatsapp')
        if not res.get("success"):
            res = SupplierAuthSecurity.generate_and_send_otp(supplier_obj, channel='email')

        if not res.get("success"):
            return jsonify({"success": False, "message": res.get("message", "فشل إرسال رمز التحقق.")}), 500

        session['reset_identifier'] = identifier
        
        masked_id = identifier[:3] + "****" + identifier[-2:] if len(identifier) > 5 else "77***89"
        return jsonify({
            "success": True,
            "otp_sent": True,
            "message": "تم إرسال رمز التحقق بنجاح إلى هاتفك أو بريدك المسجل.",
            "data": {
                "masked_phone": masked_id
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500


@suppliers_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json(force=True, silent=True) or request.form or {}
        otp_code = data.get('otp_code', '').strip()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')

        if not new_password or new_password != confirm_password:
            return jsonify({"success": False, "message": "كلمتا المرور غير متطابقتين أو غير صالحتين."}), 400

        identifier = session.get('reset_identifier')
        if not identifier:
            return jsonify({"success": False, "message": "انتهت صلاحية الجلسة، يرجى إعادة محاولة استعادة كلمة المرور."}), 400

        # التحقق من صحة الرمز الحقيقي باستخدام جدول قاعدة البيانات OTP
        verification_res = SupplierAuthSecurity.verify_supplier_otp(identifier, otp_code)
        if not verification_res.get("success"):
            return jsonify({"success": False, "message": verification_res.get("message", "رمز التحقق غير صحيح أو انتهت صلاحيته.")}), 400

        clean_phone_suffix = identifier[-9:] if identifier.isdigit() else identifier
        supplier_obj = db.session.query(Supplier).filter(
            (Supplier.username == identifier) |
            (Supplier.email == identifier) |
            (Supplier.search_phone == clean_phone_suffix) |
            (Supplier.phone == identifier)
        ).first()

        if not supplier_obj:
            return jsonify({"success": False, "message": "المورد غير موجود."}), 404

        supplier_obj.set_password(new_password)
        db.session.commit()
        session.pop('reset_identifier', None)

        return jsonify({
            "success": True,
            "message": "تم تحديث كلمة المرور بنجاح",
            "redirect_url": url_for('suppliers_bp.login')
        })
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500
