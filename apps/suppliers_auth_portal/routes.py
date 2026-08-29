from flask import render_template, request, jsonify, session, redirect
from flask_login import login_user, current_user
from apps.suppliers_auth_portal import suppliers_auth_bp
from apps.suppliers_auth_portal.seo_service import SupplierPortalSEOService
from apps.suppliers_auth_portal.registry import SupplierPortalRegistry
from apps.suppliers_auth_portal.security import (
    validate_phone_number, validate_email,
    check_rate_limit, record_failed_attempt, clear_rate_limit
)
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.extensions import db

@suppliers_auth_bp.route('/login', methods=['POST'])
def login():
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
                "redirect_url": "/supplier/dashboard"
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
                "redirect_url": "/supplier/dashboard"
            })

        else:
            return jsonify({"success": False, "message": "نوع المستخدم غير صحيح"}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500
