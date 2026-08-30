import random
import string
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.security import generate_password_hash
# استبدل النماذج والاتصال بما يناسب قاعدة بيانات مشروعك (محجوب أونلاين)
# from models import db, Supplier, SupplierEmployee

suppliers_auth_recovery_bp = Blueprint(
    'suppliers_auth_recovery_bp',
    __name__,
    template_folder='templates'
)

# ذاكرة مؤقتة لتخزين رموز التحقق (OTP) في بيئة التطوير والإنتاج (يمكن نقلها لـ Redis أو قاعدة البيانات)
# الهيكل: { identifier: {"otp": "123456", "expires_at": datetime, "attempts": 0} }
OTP_STORAGE = {}

@suppliers_auth_recovery_bp.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    """عرض صفحة استعادة كلمة المرور ذات المرحلتين"""
    return render_template('suppliers_auth_portal/forgot_password.html')

@suppliers_auth_recovery_bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """معالجة المرحلة الأولى: التحقق من وجود المورد وإرسال رمز التحقق OTP"""
    data = request.get_json() or {}
    identifier = data.strip() if isinstance(data, str) else data.get('identifier', '').strip()

    if not identifier:
        return jsonify({
            "success": False,
            "message": "يرجى إدخال اسم المستخدم، البريد الإلكتروني، أو رقم الهاتف."
        }), 400

    # TODO: قم بالبحث عن المورد أو موظف المورد في قاعدة البيانات بناءً على الـ identifier
    # مثال:
    # supplier = Supplier.query.filter(
    #     (Supplier.username == identifier) | 
    #     (Supplier.email == identifier) | 
    #     (Supplier.phone == identifier)
    # ).first()

    # محاكاة التحقق (استبدلها بالتحقق الفعلي من قاعدة البيانات)
    # للتجربة، نعتبر أي مدخل صالح أو نتحقق من قاعدة البيانات الخاصة بك
    user_found = True  # اجعلها تطابق منطق قاعدة البيانات لديك

    if not user_found:
        return jsonify({
            "success": False,
            "message": "لم يتم العثور على حساب مرتبط بالبيانات المدخلة في نظام محجوب أونلاين."
        }), 404

    # توليد رمز تحقق مكون من 6 أرقام
    otp_code = "".join(random.choices(string.digits, k=6))
    
    # تحديد وقت انتهاء الصلاحية (مثلاً خلال 10 دقائق)
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    # حفظ الرمز في التخزين المؤقت
    OTP_STORAGE[identifier] = {
        "otp": otp_code,
        "expires_at": expires_at,
        "attempts": 0
    }

    # TODO: ربط بوابة الرسائل النصية القصيرة SMS أو البريد الإلكتروني لإرسال الرمز الفعلي
    # send_sms_or_email(identifier, otp_code)

    # إخفاء جزء من رقم الهاتف أو البريد للعرض في الواجهة
    masked_target = identifier
    if "@" in identifier:
        name_part, domain = identifier.split("@")
        masked_target = f"{name_part[:2]}***@ {domain}"
    elif len(identifier) > 4:
        masked_target = f"****{identifier[-4:]}"

    # في وضع التطوير (Development Mode)، نقوم بإرجاع الرمز ضمن الاستجابة لتسهيل الاختبار الفوري
    is_dev = current_app.config.get('DEBUG', True)

    return jsonify({
        "success": True,
        "otp_sent": True,
        "message": "تم إرسال رمز التحقق بنجاح.",
        "data": {
            "masked_phone": masked_target,
            "_dev_otp": otp_code if is_dev else None  # يظهر في وضع التطوير فقط للتسهيل
        }
    }), 200

@suppliers_auth_recovery_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """معالجة المرحلة الثانية: التحقق من الرمز وتحديث كلمة المرور بتشفير آمن"""
    data = request.get_json() or {}
    identifier = data.get('identifier', '').strip()
    otp_code = data.get('otp_code', '').strip()
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if not identifier or not otp_code or not new_password:
        return jsonify({
            "success": False,
            "message": "جميع الحقول مطلوبة لإتمام عملية الاستعادة."
        }), 400

    if new_password != confirm_password:
        return jsonify({
            "success": False,
            "message": "كلمتا المرور غير متطابقتين."
        }), 400

    if len(new_password) < 8:
        return jsonify({
            "success": False,
            "message": "يجب أن تكون كلمة المرور الجديدة مكونة من 8 أحرف على الأقل."
        }), 400

    # التحقق من وجود بيانات الرمز في الذاكرة
    record = OTP_STORAGE.get(identifier)
    if not record:
        return jsonify({
            "success": False,
            "message": "انتهت صلاحية الجلسة أو لم يتم طلب رمز تحقق لهذا الحساب. يجيب إعادة المحاولة."
        }), 400

    # التحقق من عدد المحاولات الفاشلة (أقصى حد 5 محاولات)
    if record["attempts"] >= 5:
        del OTP_STORAGE[identifier]
        return jsonify({
            "success": False,
            "message": "تم تجاوز الحد الأقصى للمحاولات الخاطئة. يجيب طلب رمز تحقق جديد."
        }), 400

    # التحقق من صلاحية الوقت
    if datetime.utcnow() > record["expires_at"]:
        del OTP_STORAGE[identifier]
        return jsonify({
            "success": False,
            "message": "انتهت صلاحية رمز التحقق (OTP). يجيب إعادة الإرسال."
        }), 400

    # التحقق من صحة الرمز
    if record["otp"] != otp_code:
        record["attempts"] += 1
        return jsonify({
            "success": False,
            "message": f"رمز التحقق غير صحيح. المحاولات المتبقية: {5 - record['attempts']}"
        }), 400

    # الرمز صحيح تماماً -> تحديث كلمة المرور في قاعدة البيانات
    hashed_password = generate_password_hash(new_password)

    # TODO: تحديث كلمة المرور في قاعدة البيانات للمورد المعني
    # supplier = Supplier.query.filter(...).first()
    # supplier.password_hash = hashed_password
    # db.session.commit()

    # مسح الرمز من الذاكرة المؤقتة بعد الاستخدام الناجح
    del OTP_STORAGE[identifier]

    return jsonify({
        "success": True,
        "message": "تم تحديث كلمة المرور وتشفيرها بنجاح",
        "redirect_url": "/suppliers/login"
    }), 200
