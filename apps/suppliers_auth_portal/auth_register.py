# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_register.py

from flask import Blueprint, request, jsonify, session, url_for
from flask_login import login_user
from apps.extensions import db
from apps.models.supplier_db import Supplier

# بما أن البصمة الرئيسية للبوابة معرّفة بـ url_prefix='/supplier'، سيكون الرابط النهائي /supplier/register
auth_register_bp = Blueprint('auth_register', __name__, template_folder='templates')

@auth_register_bp.route('/register', methods=['POST'])
def register():
    """معالجة تسجيل مورد جديد والتحقق من البيانات وتخزينها وفقاً لهيكلة الجدول المعتمدة"""
    try:
        data = request.get_json(force=True, silent=True) or request.form or {}
        if not data:
            return jsonify({
                "success": False,
                "message": "بيانات الطلب غير صالحة."
            }), 400

        # استلام الحقول المرسلة من واجهة التسجيل
        company_name = data.get('company_name', '').strip()
        contact_person = data.get('contact_person', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        category = data.get('category', '').strip()
        agree_pricing_policy = data.get('agree_pricing_policy', False)

        # التحقق من الحقول الإجبارية
        if not company_name or not contact_person or not phone or not password or not category:
            return jsonify({
                "success": False,
                "message": "يرجى تعبئة كافة الحقول الإجبارية المميزة بنجمة."
            }), 400

        # التحقق من الموافقة على سياسة حوكمة الأسعار
        if not agree_pricing_policy and str(agree_pricing_policy).lower() not in ['true', '1', 'on']:
            return jsonify({
                "success": False,
                "message": "يجب الموافقة على شروط حوكمة التوريد والأسعار بسعر التكلفة للاستمرار."
            }), 400

        # استخلاص آخر 9 أرقام لمطابقة حقل search_phone المعياري الفريد
        digits_only = "".join(filter(str.isdigit, phone))
        clean_search_phone = digits_only[-9:] if len(digits_only) >= 9 else digits_only

        # التحقق من عدم تكرار رقم الهاتف أو البريد الإلكتروني مسبقاً
        existing_supplier = Supplier.query.filter(
            (Supplier.search_phone == clean_search_phone) | 
            ((Supplier.email == email) & (Supplier.email != ''))
        ).first()

        if existing_supplier:
            return jsonify({
                "success": False,
                "message": "رقم الهاتف أو البريد الإلكتروني مسجل مسبقاً في النظام."
            }), 400

        # توليد اسم مستخدم افتراضي فريد
        generated_username = f"sup_{clean_search_phone}"

        # إنشاء كائن المورد الجديد وتفعيل التشفير السيادي للهاتف
        new_supplier = Supplier(
            username=generated_username,
            email=email if email else None,
            owner_name=contact_person,
            trade_name=company_name,
            store_name=company_name,
            phone=phone,  # سيتم تشفيره وتحديث search_phone تلقائياً داخل نموذج Supplier
            status='active',
            rank='bronze'
        )
        
        # تشفير كلمة المرور بالطريقة المعتمدة في النموذج
        new_supplier.set_password(password)

        db.session.add(new_supplier)
        db.session.commit()  # سيقوم المحرك التلقائي بعد الـ insert بتوليد SUP و WEL

        # تسجيل الدخول تلقائياً عبر Flask-Login والجلسة
        login_user(new_supplier)
        session['user_type'] = 'supplier'
        session['supplier_logged_in'] = True
        session['supplier_identifier'] = generated_username

        return jsonify({
            "success": True,
            "message": "تم إنشاء الحساب والمحفظة المالية بنجاح.",
            "redirect_url": url_for('suppliers_dashboard.dashboard')
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"حدث خطأ غير متوقع في الخادم: {str(e)}"
        }), 500
