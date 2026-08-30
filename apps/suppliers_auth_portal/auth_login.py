# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_login.py

from flask import render_template, request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user
from apps.suppliers_auth_portal import suppliers_bp
from apps.suppliers_auth_portal.seo_service import SupplierPortalSEOService
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.extensions import db

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        seo = SupplierPortalSEOService.get_meta_tags("login")
        return render_template('suppliers_auth_portal/login.html', seo=seo)

    try:
        # التقاط البيانات سواء كانت JSON أو Form Data لضمان عدم حدوث فراغ
        data = request.get_json(silent=True) or request.form or {}
        
        identifier = data.get('identifier', '').strip()
        password = data.get('password', '')
        user_type = data.get('user_type', 'supplier').strip()

        print(f"DEBUG LOGIN ATTEMPT -> Type: {user_type}, Identifier: {identifier}") # للفحص في الـ Terminal

        if not identifier or not password:
            return jsonify({"success": False, "message": "يرجى إدخال اسم المستخدم/الهاتف وكلمة المرور."}), 400

        clean_phone_suffix = identifier[-9:] if identifier.isdigit() else identifier

        if user_type == 'supplier':
            supplier_obj = db.session.query(Supplier).filter(
                db.or_(
                    Supplier.username == identifier,
                    Supplier.email == identifier,
                    Supplier.search_phone == clean_phone_suffix
                )
            ).first()

            if not supplier_obj:
                return jsonify({"success": False, "message": "عذراً، المورد غير مسجل في النظام."}), 404

            if not supplier_obj.check_password(password):
                return jsonify({"success": False, "message": "كلمة المرور غير صحيحة، يرجى المحاولة مرة أخرى."}), 401

            session['user_type'] = 'supplier'
            login_user(supplier_obj, remember=True)
            session['supplier_logged_in'] = True
            session['supplier_identifier'] = identifier
            
            return jsonify({
                "success": True,
                "message": "تم تسجيل الدخول بنجاح",
                "redirect_url": url_for('suppliers_dashboard.dashboard')
            })

        elif user_type == 'employee':
            staff_filters = [
                SupplierStaff.username == identifier,
                SupplierStaff.email == identifier
            ]
            if hasattr(SupplierStaff, 'search_phone'):
                staff_filters.append(SupplierStaff.search_phone == clean_phone_suffix)
            elif hasattr(SupplierStaff, 'phone'):
                staff_filters.append(SupplierStaff.phone == identifier)

            staff_obj = db.session.query(SupplierStaff).filter(db.or_(*staff_filters)).first()

            if not staff_obj:
                return jsonify({"success": False, "message": "عذراً، موظف المورد غير مسجل."}), 404

            if not staff_obj.check_password(password):
                return jsonify({"success": False, "message": "كلمة المرور غير صحيحة للموظف."}), 401

            session['user_type'] = 'supplier_staff'
            login_user(staff_obj, remember=True)
            session['supplier_staff_logged_in'] = True
            session['supplier_identifier'] = identifier
            
            return jsonify({
                "success": True,
                "message": "تم تسجيل الدخول بنجاح",
                "redirect_url": url_for('suppliers_dashboard.dashboard')
            })

        else:
            return jsonify({"success": False, "message": "نوع المستخدم غير صالح."}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500


@suppliers_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('suppliers_bp.login'))
