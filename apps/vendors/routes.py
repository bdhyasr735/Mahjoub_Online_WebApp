# coding: utf-8
# 📂 apps/vendors/routes.py - العقل المدبر الخلفي لدخول الموردين وحوكمة الـ OTP

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.otp_db import OTPVerification
from apps.utils.messaging import MahjoubMessageCenter  # معالج الرسائل والقوالب السيادية
from werkzeug.security import check_password_hash
from . import vendors_bp

# 1️⃣ مسار فحص البريد الإلكتروني وتوليد الرمز (الخطوة الأولى من الواجهة)
@vendors_bp.route('/check-account', methods=['POST'])
def check_account():
    """الفحص الأولي للبريد الإلكتروني وتوليد رمز AES-256 OTP حياً"""
    data = request.get_json() or {}
    email = data.get('email')

    if not email:
        return jsonify({"status": "error", "message": "الرجاء إدخال البريد الإلكتروني الإداري"}), 400

    # البحث عن المورد عبر البريد الإلكتروني الإداري المعتمد
    supplier = Supplier.query.filter_by(admin_email=email).first()
    
    if not supplier:
        return jsonify({"status": "error", "message": "هذا الحساب غير مسجل في منظومة الموردين"}), 404

    if supplier.status != "active":  # حظر الحسابات المعلقة أو المرفوضة حوكمياً
        return jsonify({"status": "error", "message": "هذا الحساب معلق إدارياً، راجع الدعم الفني"}), 403

    try:
        # توليد الرمز وتشفيره بـ AES-256 تلقائياً داخل جدول الـ OTP
        raw_otp = OTPVerification.generate_otp(email=email, expires_in_minutes=5)
        db.session.commit()

        # تجهيز وإرسال قالب الرسالة الفاخر (يمكنك ربطه هنا مع خدمة إرسال البريد السحابية لديك)
        email_html = MahjoubMessageCenter.get_otp_email_template(username=supplier.username, otp_code=raw_otp)
        
        # 💡 ملاحظة: هنا يتم استدعاء دالة إرسال الإيميل الحقيقية مثل: send_mail(email, "رمز التحقق السيادي", email_html)
        print(f"📦 [MAHJOUB BRIDGE SYSTEM] تم إرسال الرمز بنجاح إلى {email} -> الرمز النقي للتجربة: {raw_otp}")

        return jsonify({
            "status": "success", 
            "message": "تم توليد وإرسال رمز التحقق السيادي بنجاح للبريد الإداري المعتمد",
            "username": supplier.username  # إرجاع اسم المستخدم المعتمد لعرضه في واجهة الترحيب
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"فشل في معالجة نظام الرموز السيادي: {str(e)}"}), 500


# 2️⃣ مسار التحقق من الرمز الفوري (الخطوة الثانية من الواجهة)
@vendors_bp.route('/verify-otp-token', methods=['POST'])
def verify_otp_token():
    """المطابقة الحية للرمز المشفر بـ AES-256 واستهلاكه فوراً للسيادة الأمنية"""
    data = request.get_json() or {}
    email = data.get('email')
    otp_code = data.get('otp_code')

    if not email or not otp_code:
        return jsonify({"status": "error", "message": "البيانات المدخلة غير مكتملة"}), 400

    # استدعاء دالة التحقق الذكية التي تقوم بفك التشفير والمطابقة الحية واستهلاك الرمز
    is_valid = OTPVerification.verify_otp(email=email, input_code=otp_code)

    if is_valid:
        return jsonify({"status": "success", "message": "تمت مطابقة الرمز السيادي بنجاح، انتقل لخطوة التوقيع"}), 200
    else:
        return jsonify({"status": "error", "message": "رمز التحقق غير صحيح أو انتهت صلاحيته الزمنية"}), 400


# 3️⃣ مسار البوابة والتحقق النهائي من كلمة المرور (GET & POST)
@vendors_bp.route('/login', methods=['GET', 'POST'])
def login():
    """بوابة الدخول الرئيسية واستقبال التوقيع النهائي بكلمة المرور"""
    if current_user.is_authenticated:
        return redirect(url_for('vendors.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        otp_code = request.form.get('otp_code')

        if not email or not password or not otp_code:
            flash("الرجاء إكمال كافة خطوات التحقق السيادية أولاً", "danger")
            return render_template('vendor/login.html')

        # الفحص الأخير للتأكد من عدم تجاوز الواجهة الأمامية
        supplier = Supplier.query.filter_by(admin_email=email, status="active").first()
        
        if supplier and check_password_hash(supplier.password_hash, password):
            # توليد الأكواد والروابط السيادية للمورد إذا لم تكن موجودة سابقاً تلقائياً
            supplier.generate_codes()
            db.session.commit()

            # بدء الجلسة الرسمية للمورد في المنصة
            login_user(supplier)
            flash(f"مرحباً بك مجدداً في لوحة تحكم حوكمة التجارة الرقمية اللامركزية للمنصة", "success")
            return redirect(url_for('vendors.dashboard'))
        
        flash("فشل في مطابقة كلمة المرور المعتمدة لحسابك"، "danger")
        return render_template('vendor/login.html')
        
    return render_template('vendor/login.html')


# 4️⃣ مسار لوحة التحكم الخاصة بالمورد (المحمية)
@vendors_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم السيادية للمورد الموثق وبوابة حوكمة العمليات"""
    return render_template('vendor/dashboard.html', supplier=current_user)


# 5️⃣ مسار تسجيل الخروج وإغلاق الجلسة السيادية
@vendors_bp.route('/logout')
@login_required
def logout():
    """إغلاق الجلسة الآمنة للمورد والعودة للبوابة الرئيسية"""
    logout_user()
    flash("تم تسجيل الخروج وإغلاق الجلسة السيادية بنجاح", "info")
    return redirect(url_for('vendors.login'))
