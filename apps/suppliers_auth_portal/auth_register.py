# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_register.py

from flask import render_template, request, jsonify, session, url_for
from flask_login import login_user
from werkzeug.security import generate_password_hash

from apps.suppliers_auth_portal import suppliers_bp
from apps.suppliers_auth_portal.seo_service import SupplierPortalSEOService
from apps.models.supplier_db import Supplier
from apps.extensions import db

@suppliers_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        seo = SupplierPortalSEOService.get_meta_tags("register")
        return render_template('suppliers_auth_portal/register.html', seo=seo)

    try:
        data = request.get_json(force=True, silent=True) or request.form or {}
        
        company_name = data.get('company_name', '').strip()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')

        if not company_name or not username or not phone or not password:
            return jsonify({"success": False, "message": "يرجى تعبئة كافة الحقول الإجبارية (اسم الشركة، اسم المستخدم، رقم الهاتف، وكلمة المرور)."}), 400

        clean_phone_suffix = phone[-9:] if phone.isdigit() else phone

        existing_supplier = db.session.query(Supplier).filter(
            (Supplier.username == username) |
            (Supplier.phone == phone) |
            (Supplier.search_phone == clean_phone_suffix) |
            (Supplier.email == email if email else False)
        ).first()

        if existing_supplier:
            return jsonify({"success": False, "message": "اسم المستخدم، البريد الإلكتروني، أو رقم الهاتف مسجل مسبقاً."}), 400

        new_supplier = Supplier(
            company_name=company_name,
            username=username,
            email=email if email else None,
            phone=phone,
            search_phone=clean_phone_suffix,
            password_hash=generate_password_hash(password),
            status='active'
        )

        db.session.add(new_supplier)
        db.session.commit()

        session['user_type'] = 'supplier'
        login_user(new_supplier)
        session['supplier_logged_in'] = True
        session['supplier_identifier'] = username

        return jsonify({
            "success": True,
            "message": "تم إنشاء الحساب بنجاح",
            "redirect_url": url_for('suppliers_dashboard.dashboard')
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500
