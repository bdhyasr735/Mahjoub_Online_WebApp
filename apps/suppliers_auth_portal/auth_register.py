from flask import Blueprint, request, jsonify
from flask_login import login_user
from werkzeug.security import generate_password_hash
from apps.extensions import db  # Assuming standard extension structure
from apps.models import Supplier  # Assuming Supplier model exists

# If defined as a Blueprint or imported in routes.py
# Assuming this module defines the registration logic or Blueprint route handler

def register_supplier_logic():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'بيانات الطلب غير صالحة.'}), 400

    company_name = data.get('company_name', '').strip()
    contact_person = data.get('contact_person', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email')
    password = data.get('password', '')
    category = data.get('category', '')
    agree_pricing_policy = data.get('agree_pricing_policy', False)

    # Validation checks
    if not company_name or not contact_person or not phone or not password or not category:
        return jsonify({'success': False, 'message': 'يرجى تعبئة كافة الحقول الإجبارية.'}), 400

    if not agree_pricing_policy:
        return jsonify({'success': False, 'message': 'يجب الموافقة على شروط حوكمة الأسعار والتوريد للاستمرار.'}), 400

    # Check if supplier with same phone already exists
    existing_supplier = Supplier.query.filter_by(phone=phone).first()
    if existing_supplier:
        return jsonify({'success': False, 'message': 'رقم الهاتف مسجل مسبقاً لحساب آخر.'}), 400

    if email:
        email = email.strip()
        existing_email = Supplier.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'success': False, 'message': 'البريد الإلكتروني مسجل مسبقاً لحساب آخر.'}), 400
    else:
        email = None

    try:
        hashed_password = generate_password_hash(password)
        
        new_supplier = Supplier(
            company_name=company_name,
            contact_person=contact_person,
            phone=phone,
            email=email,
            password_hash=hashed_password,
            category=category,
            agree_pricing_policy=agree_pricing_policy,
            is_active=True
        )

        db.session.add(new_supplier)
        db.session.commit()

        # Log in the supplier automatically after successful registration
        login_user(new_supplier)

        return jsonify({
            'success': True,
            'message': 'تم تسجيل المنشأة بنجاح',
            'redirect_url': '/supplier/dashboard'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء معالجة الطلب: {str(e)}'}), 500
