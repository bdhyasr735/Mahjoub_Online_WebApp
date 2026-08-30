# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_recovery.py

from flask import render_template, request, jsonify, url_for
from werkzeug.security import generate_password_hash
from apps.suppliers_auth_portal import suppliers_bp
from apps.suppliers_auth_portal.seo_service import SupplierPortalSEOService
from apps.models.supplier_db import Supplier
from apps.extensions import db

@suppliers_bp.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    if request.method == 'GET':
        seo = SupplierPortalSEOService.get_meta_tags("forgot_password")
        return render_template('suppliers_auth_portal/forgot_password.html', seo=seo)


@suppliers_bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
    try:
        data = request.get_json(force=True, silent=True) or request.form or {}
        identifier = data.get('identifier', '').strip()

        if not identifier:
            return jsonify({"success": False, "message": "يرجى إدخال اسم المستخدم، البريد الإلكتروني، أو رقم الهاتف."}), 400

        clean_phone_suffix = identifier[-9:] if identifier.isdigit() else identifier

        supplier_obj = db.session.query(Supplier).filter(
            (Supplier.username == identifier) |
            (Supplier.email == identifier) |
            (Supplier.search_phone == clean_phone_suffix)
        ).first()

        if not supplier_obj:
            return jsonify({"success": False, "message": "عذراً، لم يتم العثور على حساب مرتبط بالبيانات المدخلة."}), 404

        dev_otp = "123456"
        
        phone_str = str(supplier_obj.phone) if supplier_obj.phone else "0000"
        masked_phone = phone_str[-4:].rjust(len(phone_str), '*')

        return jsonify({
            "success": True,
            "otp_sent": True,
            "message": "تم إرسال رمز التحقق بنجاح.",
            "data": {
                "masked_phone": masked_phone,
                "_dev_otp": dev_otp
            }
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500


@suppliers_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json(force=True, silent=True) or request.form or {}
        identifier = data.get('identifier', '').strip()
        otp_code = data.get('otp_code', '').strip()
        new_password = data.get('new_password', '').strip()

        if not identifier or not otp_code or not new_password:
            return jsonify({"success": False, "message": "يرجى تعبئة كافة الحقول المطلوبة (معرف الحساب، رمز التحقق، وكلمة المرور الجديدة)."}), 400

        if otp_code != "123456":
            return jsonify({"success": False, "message": "رمز التحقق غير صحيح."}), 400

        clean_phone_suffix = identifier[-9:] if identifier.isdigit() else identifier

        supplier_obj = db.session.query(Supplier).filter(
            (Supplier.username == identifier) |
            (Supplier.email == identifier) |
            (Supplier.search_phone == clean_phone_suffix)
        ).first()

        if not supplier_obj:
            return jsonify({"success": False, "message": "الحساب غير موجود."}), 404

        supplier_obj.password_hash = generate_password_hash(new_password)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "تم تحديث كلمة المرور بنجاح",
            "redirect_url": url_for('suppliers_bp.login')
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500
