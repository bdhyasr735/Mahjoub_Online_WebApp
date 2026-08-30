# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_recovery.py

from flask import render_template, request, jsonify, session, url_for
from apps.suppliers_auth_portal import suppliers_bp
from apps.suppliers_auth_portal.seo_service import SupplierPortalSEOService
from apps.suppliers_auth_portal.security import SupplierAuthSecurity
from apps.models.supplier_db import Supplier
from apps.extensions import db

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
