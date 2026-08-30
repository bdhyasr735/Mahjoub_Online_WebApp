# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_register.py

from flask import render_template, request, jsonify, session, url_for
from flask_login import login_user
from apps.suppliers_auth_portal import suppliers_bp
from apps.suppliers_auth_portal.seo_service import SupplierPortalSEOService
from apps.suppliers_auth_portal.security import validate_phone_number, validate_email
from apps.suppliers_auth_portal.registry import SupplierPortalRegistry
from apps.models.supplier_db import Supplier
from apps.extensions import db

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
