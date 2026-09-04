# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/routes.py
import threading
import sys
import traceback
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from apps.models.supplier_db import Supplier
from apps.models.otp_db import OTP
from apps.extensions import db
from apps.suppliers_auth_portal.otp_service import SupplierOTPService
from apps.whatsapp_service.service import WhatsAppService

suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    template_folder='templates',
    url_prefix='/supplier'
)

@suppliers_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """تسجيل الدخول للموردين (يدعم JSON و Form)"""
    if current_user.is_authenticated:
        return redirect(url_for('suppliers_auth_bp.dashboard'))
    
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form.to_dict()
        identifier = data.get('identifier') or data.get('username')
        password = data.get('password')
        
        digits_only = "".join(filter(str.isdigit, str(identifier or '')))
        clean_9 = digits_only[-9:] if len(digits_only) >= 9 else digits_only
        
        supplier = Supplier.query.filter(
            (Supplier.username == identifier) |
            (Supplier.email == identifier) |
            (Supplier.search_phone == clean_9) |
            (Supplier.supplier_code == identifier)
        ).first()
        
        if supplier and supplier.check_password(password):
            login_user(supplier)
            return jsonify({
                "success": True,
                "message": "تم تسجيل الدخول بنجاح",
                "redirect_url": url_for('suppliers_auth_bp.dashboard')
            })
        else:
            return jsonify({
                "success": False,
                "message": "اسم المستخدم أو كلمة المرور غير صحيحة!"
            }), 401
    
    return render_template('suppliers_auth_portal/login.html')

@suppliers_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """تسجيل الموردين الجدد"""
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form.to_dict()
        username = data.get('username')
        password = data.get('password')
        owner_name = data.get('owner_name')
        store_name = data.get('store_name')
        phone = data.get('phone')
        
        try:
            supplier = Supplier(
                username=username,
                password=password,
                owner_name=owner_name,
                store_name=store_name,
                phone=phone
            )
            db.session.add(supplier)
            db.session.commit()
            flash('تم تسجيلك بنجاح!', 'success')
            return jsonify({
                "success": True,
                "message": "تم تسجيلك بنجاح",
                "redirect_url": url_for('suppliers_auth_bp.login')
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": f"حدث خطأ: {str(e)}"
            }), 400
    
    return render_template('suppliers_auth_portal/register.html')

@suppliers_auth_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """لوحة تحكم الموردين"""
    return render_template('suppliers_auth_portal/dashboard.html')

@suppliers_auth_bp.route('/forgot-password', methods=['GET'])
def forgot_password():
    """عرض صفحة استعادة كلمة المرور"""
    return render_template('suppliers_auth_portal/forgot_password.html')

@suppliers_auth_bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """طلب إرسال رمز التحقق OTP مع معالجة دقيقة للبحث في جدول الموردين المشفر"""
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        identifier = data.get('identifier', '').strip()
        
        if not identifier:
            return jsonify({"success": False, "message": "الرجاء إدخال اسم المستخدم أو رقم الهاتف."}), 400
        
        digits_only = "".join(filter(str.isdigit, str(identifier)))
        clean_9 = digits_only[-9:] if len(digits_only) >= 9 else digits_only
        
        # البحث الذكي المطابق لهيكل جدول الموردين المشفر
        supplier = Supplier.query.filter(
            (Supplier.username == identifier) | 
            (Supplier.email == identifier) | 
            (Supplier.search_phone == clean_9) |
            (Supplier.supplier_code == identifier)
        ).first()
        
        if not supplier:
            return jsonify({"success": False, "message": f"لم يتم العثور على حساب مرتبط بالبيانات المدخلة: {identifier}"}), 404
        
        # توحيد صيغة رقم الهاتف
        recipient_phone = SupplierOTPService._format_phone_number(supplier.phone)
        
        # 1. توليد وحفظ الرمز في قاعدة البيانات مباشرة وبسرعة
        otp_record, otp_code = OTP.create_otp(
            identifier=recipient_phone,
            target_id=supplier.id,
            target_type='supplier',
            expiry_seconds=300
        )
        
        message_text = f"🔐 رمز التحقق الخاص بك في منصة محجوب أونلاين هو: *{otp_code}*\nصالح لمدة 5 دقائق فقط."
        
        # التقاط سياق التطبيق للـ Thread الخلفي
        app_obj = current_app._get_current_object() if current_app else None

        # 2. دالة إرسال الواتساب في الخلفية لعدم تجميد المتصفح
        def send_whatsapp_async(phone, text, app_context):
            def task():
                try:
                    whatsapp = WhatsAppService()
                    res = whatsapp.send_message(recipient_phone=phone, text=text)
                    print(f"📬 [Background WhatsApp Sent]: {res}", file=sys.stderr)
                except Exception as ex:
                    print(f"❌ [خطأ في إرسال الواتساب بالخلفية]: {str(ex)}", file=sys.stderr)
                    traceback.print_exc()

            if app_context:
                with app_context.app_context():
                    task()
            else:
                task()

        thread = threading.Thread(
            target=send_whatsapp_async,
            args=(recipient_phone, message_text, app_obj)
        )
        thread.daemon = True
        thread.start()
        
        # 3. إرجاع الاستجابة للعميل فوراً لمنع خطأ الاتصال
        return jsonify({
            "success": True,
            "message": "تم إرسال رمز التحقق بنجاح.",
            "data": {
                "masked_phone": f"****{supplier.phone[-4:]}" if supplier.phone else "****",
                "_dev_otp": otp_code
            }
        })
        
    except Exception as e:
        print(f"❌ [خطأ في request_otp]: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"حدث خطأ داخلي: {str(e)}"}), 500

@suppliers_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """إعادة تعيين كلمة المرور باستخدام OTP"""
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        identifier = data.get('identifier', '')
        otp_code = data.get('otp_code', '')
        new_password = data.get('new_password', '')
        
        verification = SupplierOTPService.verify_otp(identifier, otp_code)
        
        if not verification.get('success'):
            return jsonify({"success": False, "message": "رمز التحقق غير صحيح أو انتهت صلاحيته."}), 400
        
        digits_only = "".join(filter(str.isdigit, str(identifier)))
        clean_9 = digits_only[-9:] if len(digits_only) >= 9 else digits_only
        
        supplier = Supplier.query.filter(
            (Supplier.username == identifier) | 
            (Supplier.email == identifier) | 
            (Supplier.search_phone == clean_9) |
            (Supplier.supplier_code == identifier)
        ).first()
        
        if not supplier:
            return jsonify({"success": False, "message": "لم يتم العثور على الحساب."}), 404
        
        supplier.password = new_password
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "تم تحديث كلمة المرور بنجاح.",
            "redirect_url": url_for('suppliers_auth_bp.login')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"حدث خطأ: {str(e)}"}), 500

@suppliers_auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('suppliers_auth_bp.login'))
