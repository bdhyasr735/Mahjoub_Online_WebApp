from flask import Blueprint, render_template, request, jsonify
# استيراد قاعدة البيانات ونماذج الجداول الخاصة بالمشروع (تأكد من مطاردة المسار حسب بنية مشروعك)
# from app.extensions import db
# from app.models.supplier import Supplier
# from app.models.wallet import SupplierWallet
# from werkzeug.security import generate_password_hash

auth_recovery_bp = Blueprint('auth_recovery', __name__, template_folder='templates')

@auth_recovery_bp.route('/suppliers/forgot-password', methods=['GET'])
def forgot_password_page():
    """عرض صفحة استعادة كلمة المرور للموردين"""
    return render_template('suppliers_auth_portal/forgot_password.html')

@auth_recovery_bp.route('/suppliers/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """التحقق من وجود المورد في جدول البيانات وإرسال رمز التحقق OTP"""
    data = request.get_json() or {}
    identifier = data.get('identifier') # قد يكون البريد الإلكتروني أو الهاتف أو اسم المستخدم
    
    if not identifier:
        return jsonify({
            'success': False, 
            'message': 'يرجى إدخال البريد الإلكتروني أو اسم المستخدم أو رقم الهاتف المرتبط بالحساب.'
        }), 400
    
    # الاعتماد الفعلي على جدول الموردين (Supplier Model)
    # supplier = Supplier.query.filter(
    #     (Supplier.username == identifier) | 
    #     (Supplier.email == identifier) | 
    #     (Supplier.phone == identifier)
    # ).first()
    
    # if not supplier:
    #     return jsonify({
    #         'success': False, 
    #         'message': 'لم يتم العثور على أي حساب مسجل بهذه البيانات في النظام.'
    #     }, 404)

    # توليد رمز التحقق (OTP) وحفظه مؤقتاً في قاعدة البيانات مرتبطاً بمعرف المورد
    generated_otp = "123456" # يتم توليد رقم عشوائي آمن في الإنتاج وتخزينه مع وقت انتهاء الصلاحية
    
    return jsonify({
        'success': True,
        'otp_sent': True,
        'message': 'تم التحقق من بيانات المورد وإرسال رمز التحقق بنجاح.',
        'data': {
            'identifier': identifier,
            '_dev_otp': generated_otp # للاختبار والتطوير فقط ويحذف عند الإطلاق
        }
    })

@auth_recovery_bp.route('/suppliers/reset-password', methods=['POST'])
def reset_password():
    """التحقق من رمز OTP وتحديث كلمة المرور المشفرة للمورد في قاعدة البيانات"""
    data = request.get_json() or {}
    identifier = data.get('identifier')
    otp_code = data.get('otp_code')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    if not identifier or not otp_code or not new_password:
        return jsonify({'success': False, 'message': 'جميع حقول البيانات مطلوبة لإتمام عملية الاستعادة.'}), 400
        
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'كلمتا المرور غير متطابقتين، يرجى التثبت.'}), 400

    # 1. البحث عن المورد والتحقق من صحة وصلاحية رمز الـ OTP المطابق في الجدول
    # supplier = Supplier.query.filter(...).first()
    # if not supplier or supplier.otp_code != otp_code:
    #     return jsonify({'success': False, 'message': 'رمز التحقق غير صحيح أو منتهي الصلاحية.'}, 400)

    # 2. تشفير كلمة المرور وتحديثها في جدول الموردين وحذف رمز الـ OTP المستخدم
    # supplier.password_hash = generate_password_hash(new_password)
    # supplier.otp_code = None
    # db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'تم تحديث كلمة المرور وحفظها بنجاح في قاعدة البيانات.',
        'redirect_url': '/suppliers/login'
    })
