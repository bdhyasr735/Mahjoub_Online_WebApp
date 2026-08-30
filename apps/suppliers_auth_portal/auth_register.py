# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_register.py

from flask import render_template, request, jsonify, session, url_for
from flask_login import login_user
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
        contact_person = data.get('contact_person', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        category = data.get('category', '').strip()

        if not company_name or not contact_person or not phone or not password or not category:
            return jsonify({"success": False, "message": "يرجى استكمال جميع الحقول الإلزامية."}), 400

        # التحقق من عدم تكرار رقم الهاتـف أو البريد
        clean_phone_suffix = phone[-9:] if phone.isdigit() else phone
        existing_supplier = db.session.query(Supplier).filter(
            (Supplier.phone == phone) | 
            (Supplier.search_phone == clean_phone_suffix) | 
            (Supplier.email == email if email else False)
        ).first()

        if existing_supplier:
            return jsonify({"success": False, "message": "رقم الهاتف أو البريد الإلكتروني مسجل مسبقاً."}), 400

        # إنشاء المورد الجديد مباشرة بشكل صريح
        new_supplier = Supplier(
            company_name=company_name,
            owner_name=contact_person,
            phone=phone,
            search_phone=clean_phone_suffix,
            email=email if email else None,
            category=category
        )
        new_supplier.set_password(password)

        db.session.add(new_supplier)
        db.session.commit()

        # تسجيل الدخول تلقائياً بعد التسجيل الناجح
        session['user_type'] = 'supplier'
        login_user(new_supplier)
        session['supplier_logged_in'] = True
        session['supplier_identifier'] = phone

        return jsonify({
            "success": True,
            "message": "تم إنشاء الحساب ولوحة التحكم بنجاح.",
            "redirect_url": url_for('suppliers_dashboard.dashboard')
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"خطأ داخلي في الخادم: {str(e)}"}), 500
