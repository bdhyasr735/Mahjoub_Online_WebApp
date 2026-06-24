# coding: utf-8
# 📂 apps/suppliers_auth_portal/routes.py - نظام الدخول للموردين والمسوقين (نسخة HyperSend V2 المحصنة)

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from flask_login import login_user, logout_user, current_user
from apps.extensions import db  
import uuid
import time

suppliers_bp = Blueprint('suppliers', __name__, template_folder='templates')

def format_phone(phone):
    phone = "".join(filter(str.isdigit, str(phone)))
    if len(phone) == 9 and phone.startswith('7'):
        return '967' + phone
    if len(phone) == 10 and phone.startswith('07'):
        return '967' + phone[1:]
    return phone

class SupplierDispatcher:
    @staticmethod
    def send(phone, code):
        from apps.suppliers_auth_portal.auth_service import VendorAuthService
        return VendorAuthService.initiate_login(phone, code)

@suppliers_bp.before_request
def check_login():
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
        return render_template('suppliers_auth_portal/login.html')

    from apps.models.otp_db import OTPVerification
    try:
        data = request.get_json() if request.is_json else request.form
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

        # --- دخول الموردين مع حماية Cooldown ---
        phone = format_phone(data.get('phone', ''))
        if not phone:
            return jsonify({"status": "error", "message": "رقم الهاتف مطلوب"}), 400

        # حماية: منع طلب أكثر من رمز في أقل من 60 ثانية
        last_otp = session.get('last_otp_sent', 0)
        if time.time() - last_otp < 60:
            return jsonify({"status": "error", "message": "يرجى الانتظار دقيقة قبل طلب رمز جديد"}), 429

        if OTPVerification.generate_otp(phone, SupplierDispatcher):
            session['last_otp_sent'] = time.time()
            return jsonify({"status": "success", "message": "تم إرسال رمز التحقق بنجاح"})
        
        return jsonify({"status": "error", "message": "فشل إرسال الرمز، يرجى المحاولة لاحقاً"}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "حدث خطأ فني"}), 500

@suppliers_bp.route('/verify', methods=['GET', 'POST'])
def verify_page():
    if current_user.is_authenticated:
        return redirect(url_for('suppliers.dashboard'))
        
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/verify.html')

    from apps.models.otp_db import OTPVerification
    try:
        data = request.get_json() if request.is_json else request.form
        phone = format_phone(data.get('phone', ''))
        otp = data.get('otp')

        if not phone or not otp:
            return jsonify({"status": "error", "message": "بيانات التحقق غير مكتملة"}), 400

        if OTPVerification.verify_otp(phone, otp):
            from apps.models import Supplier
            supplier = Supplier.query.filter_by(phone=phone).first()
            
            if not supplier:
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

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "حدث خطأ أثناء فحص رمز التحقق"}), 500

@suppliers_bp.route('/dashboard')
def dashboard():
    return "مرحباً بك في لوحة تحكم الموردين لمنصة محجوب أونلاين"

@suppliers_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('suppliers.login'))
