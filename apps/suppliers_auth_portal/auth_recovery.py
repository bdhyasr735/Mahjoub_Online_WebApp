# -*- coding: utf-8 -*-
from flask import request, jsonify
from werkzeug.security import generate_password_hash
# قم بتعديل مسار استيراد نموذج المورد وقاعدة البيانات بما يتطابق مع هيكل مشروعك الفعلي
from apps.models import Supplier
from apps.extensions import db

def request_otp_logic():
    # دعم قراءة البيانات سواء كانت JSON أو Form Data
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({'success': False, 'message': 'بيانات الطلب غير صالحة.'}), 400

    identifier = data.get('identifier', '').strip()
    if not identifier:
        return jsonify({'success': False, 'message': 'يرجى إدخال البريد الإلكتروني أو رقم الهاتف.'}), 400

    supplier = Supplier.query.filter(
        (Supplier.phone == identifier) | (Supplier.email == identifier)
    ).first()

    if not supplier:
        return jsonify({'success': False, 'message': 'عذراً، لم يتم العثور على حساب مرتبط بالبيانات المدخلة.'}), 404

    # رمز تحقق تجريبي (يمكن ربطه لاحقاً بخدمة إرسال رسائل حقيقية)
    dev_otp = "123456"

    # تنسيق رقم الهاتف لإظهار آخر 4 أرقام فقط إن وجد
    phone_str = str(supplier.phone) if supplier.phone else "0000"
    masked_phone = phone_str[-4:].rjust(len(phone_str), '*')

    return jsonify({
        'success': True,
        'otp_sent': True,
        'message': 'تم إرسال رمز التحقق بنجاح.',
        'data': {
            'masked_phone': masked_phone,
            '_dev_otp': dev_otp
        }
    }), 200

def reset_password_logic():
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({'success': False, 'message': 'بيانات الطلب غير صالحة.'}), 400

    identifier = data.get('identifier', '').strip()
    otp_code = data.get('otp_code', '').strip()
    new_password = data.get('new_password', '').strip()

    if not otp_code or not new_password:
        return jsonify({'success': False, 'message': 'يرجى إدخال رمز التحقق وكلمة المرور الجديدة.'}), 400

    if otp_code != "123456":
        return jsonify({'success': False, 'message': 'رمز التحقق غير صحيح.'}), 400

    supplier = Supplier.query.filter(
        (Supplier.phone == identifier) | (Supplier.email == identifier)
    ).first()

    if not supplier:
        return jsonify({'success': False, 'message': 'الحساب غير موجود.'}), 404

    try:
        supplier.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'تم تحديث كلمة المرور بنجاح',
            'redirect_url': '/suppliers/login'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء التحديث: {str(e)}'}), 500
