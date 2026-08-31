# apps/auth_portal/routes.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_wtf.csrf import generate_csrf
# افتراض استيراد النماذج ووحدات التحقق الخاصة بالخادم (تأكد من مطابقتها لهيكلة مشروعك)

auth_portal = Blueprint('auth_portal', __name__, template_folder='templates')

@auth_portal.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # توليد وإرسال صفحة تسجيل الدخول السيادية
        return render_template('auth/login.html')
    
    # معالجة طلب الـ POST القادم من الواجهة الأمامية (AJAX)
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    step = data.get('step', 'credentials')
    otp_code = data.get('otp_code')
    
    # مثال للمنطق البرمجي (يتم ربطه بقواعد البيانات والتحقق الفعلي للمشرفين)
    if step == 'credentials':
        # تحقق مبدئي من اسم المستخدم وكلمة المرور (استبدل الشروط بمنطق قاعدة البيانات الخاص بك)
        if username == "admin" and password == "secure_admin_password":
            # تفعيل خطوة طلب الرمز الثنائي OTP
            session['pre_auth_admin'] = username
            return jsonify({
                "status": "require_otp",
                "message": "تم التحقق من بيانات الدخول بنجاح. يرجى إدخال رمز التحقق السيادي (OTP)."
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "بيانات الدخول الإدارية غير صحيحة."
            }), 401

    elif step == 'verify_otp':
        # التحقق من أن المستخدم مر بمرحلة بيانات الدخول الصحيحة أولاً
        if 'pre_auth_admin' not in session:
            return jsonify({
                "status": "error",
                "message": "جلسة غير صالحة، يرجى إعادة المحاولة."
            }), 400
            
        # التحقق من صحة رمز الـ OTP (مثال تجريبي: الرمز هو 123456)
        if otp_code == "123456":
            session.pop('pre_auth_admin', None)
            session['admin_logged_in'] = True
            session['admin_user'] = username
            
            return jsonify({
                "status": "success",
                "message": "تم المصادقة بنجاح، جاري التوجيه...",
                "redirect": url_for('auth_portal.dashboard')
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "رمز التحقق السيادي (OTP) غير صحيح."
            }), 400

    return jsonify({
        "status": "error",
        "message": "طلب غير صالح."
    }), 400


@auth_portal.route('/dashboard')
def dashboard():
    # حماية المسار للتأكد من أن المشرف قام بتسجيل الدخول بنجاح
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth_portal.login'))
    
    return "مرحباً بك في لوحة التحكم السيادية للإدارة - محجوب أونلاين"
