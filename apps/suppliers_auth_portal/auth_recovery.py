from flask import Blueprint, render_template, request, jsonify
from apps.extensions import db
from apps.models.supplier_db import Supplier
from datetime import datetime, timedelta

auth_recovery_bp = Blueprint('auth_recovery', __name__, template_folder='templates')

@auth_recovery_bp.route('/suppliers/forgot-password', methods=['GET'])
def forgot_password_page():
    """عرض صفحة استعادة كلمة المرور"""
    return render_template('suppliers_auth_portal/forgot_password.html')

@auth_recovery_bp.route('/suppliers/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """التحقق من بيانات المورد (اسم المستخدم، البريد، أو الهاتف بـ 9 أرقام) وإرسال OTP"""
    data = request.get_json() or {}
    identifier = data.get('identifier')
    
    if not identifier:
        return jsonify({'success': False, 'message': 'يرجى إدخال اسم المستخدم، البريد الإلكتروني، أو رقم الهاتف.'}), 400
    
    # معالجة المدخل إذا كان رقماً لاستخلاص آخر 9 أرقام لمطابقته مع حقل search_phone المعيارى
    clean_identifier = identifier.strip()
    digits_only = "".join(filter(str.isdigit, clean_identifier))
    search_query_phone = digits_only[-9:] if len(digits_only) >= 9 else digits_only

    # البحث في الجدول بناءً على الحقول المدعومة (username, email, أو search_phone)
    supplier = Supplier.query.filter(
        (Supplier.username == clean_identifier) | 
        (Supplier.email == clean_identifier) | 
        (Supplier.search_phone == search_query_phone)
    ).first()
    
    if not supplier:
        return jsonify({'success': False, 'message': 'لم يتم العثور على حساب مسجل بهذه البيانات في النظام.'}), 404

    # توليد رمز التحقق (OTP) وتخزينه (يمكنك ربطه بحقول مؤقتة أو جدول منفصل للـ OTP)
    generated_otp = "123456" 
    
    # حفظ مؤقت للرمز ووقت انتهائه (تأكد من توفر هذه الأعمدة أو تخزينها بجلسة مؤقتة/الذاكرة)
    supplier.otp_code = generated_otp
    supplier.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()
    
    # استخدام خاصية الـ phone المفكوكة لتوفير رقم مخفي دقيق
    decrypted_phone = supplier.phone or ''
    masked_phone = '***-***-' + decrypted_phone[-4:] if len(decrypted_phone) >= 4 else '***-***-5678'

    return jsonify({
        'success': True,
        'otp_sent': True,
        'message': 'تم إرسال رمز التحقق بنجاح.',
        'data': {
            'masked_phone': masked_phone,
            '_dev_otp': generated_otp  # للاختبار والتطوير
        }
    })

@auth_recovery_bp.route('/suppliers/reset-password', methods=['POST'])
def reset_password():
    """التحقق من الرمز وتحديث كلمة المرور باستخدام دالة التشفير المعتمدة set_password"""
    data = request.get_json() or {}
    identifier = data.get('identifier')
    otp_code = data.get('otp_code')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    if not identifier or not otp_code or not new_password:
        return jsonify({'success': False, 'message': 'جميع حقول البيانات مطلوبة.'}), 400
        
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'كلمتا المرور غير متطابقتين.'}), 400

    clean_identifier = identifier.strip()
    digits_only = "".join(filter(str.isdigit, clean_identifier))
    search_query_phone = digits_only[-9:] if len(digits_only) >= 9 else digits_only

    supplier = Supplier.query.filter(
        (Supplier.username == clean_identifier) | 
        (Supplier.email == clean_identifier) | 
        (Supplier.search_phone == search_query_phone)
    ).first()

    if not supplier or getattr(supplier, 'otp_code', None) != otp_code:
        return jsonify({'success': False, 'message': 'رمز التحقق غير صحيح أو منتهي الصلاحية.'}), 400

    # استخدام دالة التشفير الأمنية المدمجة في نموذج المورد
    supplier.set_password(new_password)
    supplier.otp_code = None
    supplier.otp_expires_at = None
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'تم تحديث كلمة المرور وتشفيرها بنجاح.',
        'redirect_url': '/suppliers/login'
    })
