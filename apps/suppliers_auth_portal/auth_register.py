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
        contact_person = data.get('contact_person', '').strip() or data.get('owner_name', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not company_name or not phone or not password:
            return jsonify({"success": False, "message": "يرجى استكمال الحقول الإلزامية الأساسية (اسم المنشأة، الهاتف، كلمة المرور)."}), 400

        # التحقق من عدم تكرار رقم الهاتف
        clean_phone_suffix = phone[-9:] if phone.isdigit() else phone
        existing_supplier = db.session.query(Supplier).filter(
            (Supplier.search_phone == clean_phone_suffix) | 
            (Supplier.email == email if email else False)
        ).first()

        if existing_supplier:
            return jsonify({"success": False, "message": "رقم الهاتف أو البريد الإلكتروني مسجل مسبقاً."}), 400

        # توليد اسم مستخدم فريد وصريح يعتمد على رقم الهاتف أو الأجزاء المتاحة
        base_username = f"sup_{clean_phone_suffix}"
        username = base_username
        counter = 1
        while db.session.query(Supplier).filter_by(username=username).first():
            username = f"{base_username}_{counter}"
            counter += 1

        # إنشاء المورد الجديد مع مطابقة الحقول الفعليه للنموذج
        new_supplier = Supplier(
            username=username,
            store_name=company_name,
            trade_name=company_name,
            owner_name=contact_person if contact_person else None,
            phone=phone,
            email=email if email else None,
            status='active'
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
