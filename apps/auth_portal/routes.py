# apps/auth_portal/routes.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, abort

auth_portal = Blueprint('auth_portal', __name__, template_folder='templates')

# المسار السيادي السري الحقيقي لتسجيل الدخول
SECRET_ADMIN_PATH = '/m7jb_sovereign_hq_v2_99x'

@auth_portal.route(SECRET_ADMIN_PATH, methods=['GET', 'POST'])
def secure_admin_login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    step = data.get('step', 'credentials')
    otp_code = data.get('otp_code')
    
    if step == 'credentials':
        if username == "admin" and password == "secure_admin_password":
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
        if 'pre_auth_admin' not in session:
            return jsonify({
                "status": "error",
                "message": "جلسة غير صالحة، يرجى إعادة المحاولة."
            }), 400
            
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


# مسار تمويهي (يظهر للمتطفلين كأن الصفحة غير موجودة أو يقودهم لصفحة وهمية)
@auth_portal.route('/login', methods=['GET', 'POST'])
def fake_login():
    # يمكنك إرجاع خطأ 404 لتمويه أي متطفل يحاول البحث عن صفحة تسجيل الدخول بالطرق التقليدية
    abort(404)


@auth_portal.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth_portal.secure_admin_login'))
    
    return "مرحباً بك في لوحة التحكم السيادية للإدارة - محجوب أونلاين"
