# coding: utf-8
# 📂 apps/suppliers_auth_portal/routes.py - نظام الدخول السيادي (النسخة النهائية الكاملة والمصححة)

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from flask_login import login_user, logout_user, current_user
from apps.extensions import db  
import uuid

# استيراد خدمة الإرسال الخاصة بالموردين لربطها بالموجه
from apps.suppliers_auth_portal.auth_service import VendorAuthService

# تعريف الـ Blueprint باسم 'suppliers'
suppliers_bp = Blueprint('suppliers', __name__, template_folder='templates')

# جسر إرسال الموردين المستقل (لمنع التداخل مع الإدارة السيادية)
class SupplierDispatcher:
    @staticmethod
    def send(phone, code):
        return VendorAuthService.initiate_login(phone, code)

@suppliers_bp.before_request
def check_login():
    """حماية سيادية: فحص الحماية فقط إذا كان الطلب يخص مستخدم غير مسجل وموجه لهذا الـ Blueprint"""
    # 🔄 تم إضافة 'suppliers.verify_page' هنا حتى لا يطرد النظام المستخدم أثناء التحقق من الرمز
    if request.endpoint in ['suppliers.login', 'suppliers.verify_page', 'static'] or not request.blueprint == 'suppliers':
        return None
    
    if request.endpoint and 'marketers' in request.endpoint:
        return None

    if not current_user.is_authenticated:
        return redirect(url_for('suppliers.login'))

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('suppliers.dashboard'))
        # الإبقاء على المسار الهيكلي الصحيح ليتطابق مع مكان وجود الملف تماماً
        return render_template('suppliers_auth_portal/login.html')

    from apps.models.otp_db import OTPVerification

    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        if not data:
            return jsonify({"status": "error", "message": "بيانات غير صالحة"}), 400

        login_type = data.get('type')
        
        # --- دخول المسوقين ---
        if login_type == 'marketer':
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            from apps.models import Marketer
            user = Marketer.query.filter_by(marketing_code=username).first()
            if user and hasattr(user, 'check_password') and user.check_password(password): 
                login_user(user, remember=True)
                return jsonify({"status": "success", "redirect": url_for('marketers.dashboard')})
            return jsonify({"status": "error", "message": "بيانات الدخول غير صحيحة"}), 401

        # --- دخول الموردين ---
        raw_phone = data.get('phone', '')
        phone = "".join(filter(str.isdigit, raw_phone))
        otp = data.get('otp')

        if not phone:
            return jsonify({"status": "error", "message": "رقم الهاتف مطلوب"}), 400

        # تحويل الرقم للصيغة الدولية
        if len(phone) == 9 and phone.startswith('7'):
            phone = '967' + phone
        elif len(phone) == 10 and phone.startswith('07'):
            phone = '967' + phone[1:]

        # خطوة 1: طلب توليد وإرسال الـ OTP باستخدام الموجه الخاص بالموردين
        if phone and not otp:
            # تمرير SupplierDispatcher هنا هو السر لكي تظهر وتعمل بوابة الموردين بشكل مستقل!
            new_otp = OTPVerification.generate_otp(phone, SupplierDispatcher)
            if new_otp:
                return jsonify({"status": "success", "message": "تم إرسال رمز التحقق بنجاح عبر الواتساب"})
            return jsonify({"status": "error", "message": "فشل إرسال الرمز، يرجى المحاولة لاحقاً"}), 500

        # خطوة 2: التحقق الفعلي وتسجيل الدخول
        if phone and otp:
            if OTPVerification.verify_otp(phone, otp):
                from apps.models import Supplier
                supplier = Supplier.query.filter_by(phone=phone).first()
                
                if not supplier:
                    # ميزة الدمج الذكي: تسجيل المورد الجديد تلقائياً إذا لم يكن مسجلاً
                    supplier = Supplier(
                        username=f"supplier_{uuid.uuid4().hex[:8]}",
                        supplier_code=f"VEN-{uuid.uuid4().hex[:6].upper()}",
                        phone=phone, 
                        trade_name="مورد جديد لدينا"
                    )
                    db.session.add(supplier)
                    db.session.commit()
                
                login_user(supplier, remember=True)
                session.permanent = True
                return jsonify({"status": "success", "redirect": url_for('suppliers.dashboard')})
            
            return jsonify({"status": "error", "message": "رمز التحقق منتهي أو خاطئ"}), 400

        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400

    except Exception as e:
        db.session.rollback()
        print(f"🚨 [Supplier Auth Error]: {str(e)}")
        return jsonify({"status": "error", "message": "حدث خطأ فني في خادم المصادقة"}), 500

# 🔄 الموجه المضاف لعرض صفحة التحقق المستقلة للـ OTP
@suppliers_bp.route('/verify', methods=['GET'])
def verify_page():
    if current_user.is_authenticated:
        return redirect(url_for('suppliers.dashboard'))
    return render_template('suppliers_auth_portal/verify.html')

@suppliers_bp.route('/dashboard')
def dashboard():
    return "مرحباً بك في لوحة تحكم الموردين لمنصة محجوب أونلاين"

@suppliers_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('suppliers.login'))
