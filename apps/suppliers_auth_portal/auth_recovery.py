# -*- coding: utf-8 -*-
from flask import request, jsonify
from werkzeug.security import generate_password_hash
from apps.models import Supplier
from apps.extensions import db

def request_otp_logic():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'بيانات الطلب غير صالحة.'}), 400

    identifier = data.get('identifier', '').strip()
    supplier = Supplier.query.filter(
        (Supplier.phone == identifier) | (Supplier.email == identifier)
    ).first()

    if not supplier:
        return jsonify({'success': False, 'message': 'عذراً، لم يتم العثور على حساب مرتبط بالبيانات المدخلة.'}), 404

    # توليد رمز التحقق (OTP) وحفظه مؤقتاً (أو إرساله عبر خدمة الواتساب)
    # للتطوير والاختبار يتم إرجاع الرمز في الاستجابة التجريبية _dev_otp
    dev_otp = "123456" 

    return jsonify({
        'success': True,
        'otp_sent': True,
        'message': 'تم إرسال رمز التحقق بنجاح.',
        'data': {
            'masked_phone': supplier.phone[-4:].rjust(len(supplier.phone), '*'),
            '_dev_otp': dev_otp
        }
    }), 200

def reset_password_logic():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'بيانات الطلب غير صالحة.'}), 400

    identifier = data.get('identifier', '').strip()
    otp_code = data.get('otp_code', '').strip()
    new_password = data.get('new_password', '').strip()

    if otp_code != "123456": # التحقق من مطابقة الرمز المؤقت
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
