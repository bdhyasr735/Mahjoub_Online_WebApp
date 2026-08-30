# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_register.py
# محرك التسجيل - يدعم تسجيل الموردين الجدد مع تشفير متكامل

import re
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for, current_app
from flask_login import login_user
from sqlalchemy import or_
from werkzeug.security import generate_password_hash

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.supplier_wallet_db import SupplierWallet
from apps.forms.supplier.register_form import RegisterForm

# إنشاء بلو برنت
bp = Blueprint('auth_register', __name__, url_prefix='/supplier')


# ============================================================
# دوال مساعدة
# ============================================================

def extract_phone_digits(value):
    """استخراج آخر 9 أرقام من قيمة نصية للبحث في search_phone"""
    if not value:
        return None
    digits = ''.join(filter(str.isdigit, str(value)))
    return digits[-9:] if len(digits) >= 9 else digits


def generate_supplier_code(supplier_id):
    """توليد كود المورد بصيغة SUP-963X"""
    return f"SUP-963{supplier_id}"


def generate_wallet_code(supplier_id):
    """توليد كود المحفظة بصيغة WEL-963X"""
    return f"WEL-963{supplier_id}"


def validate_phone(phone):
    """التحقق من صحة رقم الهاتف (يحتوي على 9 أرقام على الأقل)"""
    if not phone:
        return False
    digits = ''.join(filter(str.isdigit, str(phone)))
    return len(digits) >= 9


def normalize_phone(phone):
    """تطبيع رقم الهاتف (استخراج الأرقام فقط)"""
    if not phone:
        return None
    return ''.join(filter(str.isdigit, str(phone)))


def is_phone_unique(phone):
    """التحقق من عدم وجود رقم الهاتف مسبقاً"""
    if not phone:
        return True
    search_phone = extract_phone_digits(phone)
    if not search_phone:
        return True
    # البحث في الموردين
    existing_supplier = Supplier.query.filter_by(search_phone=search_phone).first()
    if existing_supplier:
        return False
    # البحث في موظفي الموردين
    existing_staff = SupplierStaff.query.filter_by(search_phone=search_phone).first()
    if existing_staff:
        return False
    return True


def is_username_unique(username):
    """التحقق من عدم وجود اسم المستخدم مسبقاً"""
    if not username:
        return True
    # البحث في الموردين
    existing_supplier = Supplier.query.filter_by(username=username).first()
    if existing_supplier:
        return False
    # البحث في موظفي الموردين
    existing_staff = SupplierStaff.query.filter_by(username=username).first()
    if existing_staff:
        return False
    return True


def is_email_unique(email):
    """التحقق من عدم وجود البريد الإلكتروني مسبقاً"""
    if not email:
        return True
    # البحث في الموردين
    existing_supplier = Supplier.query.filter_by(email=email).first()
    if existing_supplier:
        return False
    # البحث في موظفي الموردين (فك التشفير)
    all_staff = SupplierStaff.query.all()
    for staff in all_staff:
        if staff.email and staff.email == email:
            return False
    return True


# ============================================================
# المسارات
# ============================================================

@bp.route('/register', methods=['GET'])
def register_page():
    """صفحة تسجيل مورد جديد"""
    if current_user.is_authenticated:
        return redirect(url_for('supplier.dashboard'))
    
    form = RegisterForm()
    return render_template('suppliers_auth_portal/register.html', form=form)


@bp.route('/register', methods=['POST'])
def register():
    """
    معالجة طلب تسجيل مورد جديد
    POST: { trade_name, owner_name, username, phone, email, store_name, password, confirm_password, category, agree_pricing_policy }
    """
    try:
        # التحقق من صحة النموذج
        form = RegisterForm()
        
        if not form.validate_on_submit():
            return jsonify({
                'success': False,
                'message': 'بيانات التسجيل غير صالحة',
                'errors': form.errors
            }), 400
        
        # استخراج البيانات
        trade_name = form.trade_name.data.strip()
        owner_name = form.owner_name.data.strip()
        username = form.username.data.strip()
        phone = form.phone.data.strip()
        email = form.email.data.strip() if form.email.data else None
        store_name = form.store_name.data.strip() if form.store_name.data else trade_name
        password = form.password.data
        category = form.category.data
        agree_pricing_policy = form.agree_pricing_policy.data
        
        # التحقق من الموافقة على سياسة التسعير
        if not agree_pricing_policy:
            return jsonify({
                'success': False,
                'message': 'يجب الموافقة على شروط حوكمة الأسعار للتسجيل'
            }), 400
        
        # التحقق من رقم الهاتف
        if not validate_phone(phone):
            return jsonify({
                'success': False,
                'message': 'رقم الهاتف يجب أن يحتوي على 9 أرقام على الأقل'
            }), 400
        
        # التحقق من عدم تكرار رقم الهاتف
        if not is_phone_unique(phone):
            return jsonify({
                'success': False,
                'message': 'رقم الهاتف مسجل مسبقاً. يرجى استخدام رقم آخر.'
            }), 400
        
        # التحقق من عدم تكرار اسم المستخدم
        if not is_username_unique(username):
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم موجود مسبقاً. يرجى اختيار اسم آخر.'
            }), 400
        
        # التحقق من عدم تكرار البريد الإلكتروني (إذا تم تقديمه)
        if email and not is_email_unique(email):
            return jsonify({
                'success': False,
                'message': 'البريد الإلكتروني مسجل مسبقاً. يرجى استخدام بريد آخر.'
            }), 400
        
        # إنشاء كائن المورد الجديد
        supplier = Supplier(
            username=username,
            email=email,
            owner_name=owner_name,
            trade_name=trade_name,
            store_name=store_name,
            status='pending',  # يحتاج إلى توثيق
            rank='bronze'
        )
        
        # تعيين رقم الهاتف (يتم تشفيره تلقائياً)
        supplier.phone = phone
        
        # تعيين كلمة المرور (يتم تشفيرها)
        supplier.set_password(password)
        
        # إضافة إلى قاعدة البيانات
        db.session.add(supplier)
        db.session.flush()  # للحصول على ID قبل commit
        
        # إنشاء المحفظة المرتبطة
        wallet = SupplierWallet(
            supplier_id=supplier.id,
            wallet_code=generate_wallet_code(supplier.id),
            balance=0,
            currency='YER'
        )
        db.session.add(wallet)
        
        # إنشاء كود المورد (سيتم تحديثه تلقائياً عن طريق event listener)
        # ولكننا نقوم بتحديثه يدوياً للتأكد
        supplier.supplier_code = generate_supplier_code(supplier.id)
        
        # حفظ جميع التغييرات
        db.session.commit()
        
        # تسجيل نجاح التسجيل
        current_app.logger.info(f'تسجيل مورد جديد: {username} - ID: {supplier.id}')
        
        # توليد OTP للتحقق (سيتم إرساله عبر البريد أو WhatsApp)
        otp_code = generate_otp_for_verification(supplier)
        
        # تخزين OTP في الجلسة للتحقق لاحقاً
        session['verification_supplier_id'] = supplier.id
        session['verification_otp'] = otp_code
        session['verification_created_at'] = datetime.utcnow().isoformat()
        
        # إرسال OTP للتحقق
        send_verification_otp(supplier, otp_code)
        
        # تسجيل الدخول تلقائياً
        login_user(supplier)
        
        return jsonify({
            'success': True,
            'message': 'تم تسجيل المنشأة بنجاح. تم إرسال رمز التحقق لتوثيق الحساب.',
            'redirect_url': url_for('auth_recovery.verify', 
                                   identifier=username,
                                   user_type='supplier'),
            'data': {
                'supplier_id': supplier.id,
                'username': supplier.username,
                'supplier_code': supplier.supplier_code,
                'wallet_code': wallet.wallet_code,
                'status': supplier.status,
                '_dev_otp': otp_code if current_app.debug else None
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'خطأ في تسجيل مورد جديد: {str(e)}')
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'حدث خطأ أثناء معالجة طلب التسجيل. يرجى المحاولة مرة أخرى.'
        }), 500


@bp.route('/register/check-username', methods=['POST'])
def check_username():
    """
    التحقق من توفر اسم المستخدم (AJAX)
    POST: { username }
    """
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({
                'available': False,
                'message': 'يرجى إدخال اسم المستخدم'
            }), 400
        
        if len(username) < 3:
            return jsonify({
                'available': False,
                'message': 'اسم المستخدم يجب أن يكون 3 أحرف على الأقل'
            }), 400
        
        is_available = is_username_unique(username)
        
        return jsonify({
            'available': is_available,
            'message': 'اسم المستخدم متاح' if is_available else 'اسم المستخدم غير متاح'
        })
        
    except Exception as e:
        current_app.logger.error(f'خطأ في التحقق من اسم المستخدم: {str(e)}')
        return jsonify({
            'available': False,
            'message': 'حدث خطأ أثناء التحقق'
        }), 500


@bp.route('/register/check-phone', methods=['POST'])
def check_phone():
    """
    التحقق من توفر رقم الهاتف (AJAX)
    POST: { phone }
    """
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        
        if not phone:
            return jsonify({
                'available': False,
                'message': 'يرجى إدخال رقم الهاتف'
            }), 400
        
        if not validate_phone(phone):
            return jsonify({
                'available': False,
                'message': 'رقم الهاتف يجب أن يحتوي على 9 أرقام على الأقل'
            }), 400
        
        is_available = is_phone_unique(phone)
        
        return jsonify({
            'available': is_available,
            'message': 'رقم الهاتف متاح' if is_available else 'رقم الهاتف مسجل مسبقاً'
        })
        
    except Exception as e:
        current_app.logger.error(f'خطأ في التحقق من رقم الهاتف: {str(e)}')
        return jsonify({
            'available': False,
            'message': 'حدث خطأ أثناء التحقق'
        }), 500


@bp.route('/register/check-email', methods=['POST'])
def check_email():
    """
    التحقق من توفر البريد الإلكتروني (AJAX)
    POST: { email }
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({
                'available': True,
                'message': 'البريد الإلكتروني اختياري'
            })
        
        # التحقق من صيغة البريد الإلكتروني
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({
                'available': False,
                'message': 'صيغة البريد الإلكتروني غير صحيحة'
            }), 400
        
        is_available = is_email_unique(email)
        
        return jsonify({
            'available': is_available,
            'message': 'البريد الإلكتروني متاح' if is_available else 'البريد الإلكتروني مسجل مسبقاً'
        })
        
    except Exception as e:
        current_app.logger.error(f'خطأ في التحقق من البريد الإلكتروني: {str(e)}')
        return jsonify({
            'available': False,
            'message': 'حدث خطأ أثناء التحقق'
        }), 500


# ============================================================
# دوال إرسال OTP للتحقق
# ============================================================

def generate_otp_for_verification(supplier):
    """توليد OTP للتحقق من الحساب"""
    import secrets
    return ''.join(secrets.choice('0123456789') for _ in range(6))


def send_verification_otp(supplier, otp_code):
    """
    إرسال OTP للتحقق عبر WhatsApp والبريد الإلكتروني
    """
    # إرسال عبر WhatsApp
    try:
        phone_digits = extract_phone_digits(supplier.phone)
        if phone_digits and len(phone_digits) >= 9:
            send_whatsapp_verification(phone_digits, otp_code, supplier.trade_name)
    except Exception as e:
        current_app.logger.error(f'فشل إرسال OTP للتحقق عبر WhatsApp: {str(e)}')
    
    # إرسال عبر البريد الإلكتروني (إذا كان موجوداً)
    if supplier.email:
        try:
            send_email_verification(supplier.email, otp_code, supplier.trade_name)
        except Exception as e:
            current_app.logger.error(f'فشل إرسال OTP للتحقق عبر البريد: {str(e)}')
    
    # في بيئة التطوير، طباعة الرمز
    if current_app.debug:
        print(f'🔐 OTP للتحقق - {supplier.username}: {otp_code}')
    
    return True


def send_whatsapp_verification(phone_number, otp_code, supplier_name):
    """
    إرسال OTP للتحقق عبر WhatsApp
    """
    # TODO: تكامل مع خدمة WhatsApp Business API
    current_app.logger.info(f'[WhatsApp] إرسال OTP للتحقق {otp_code} إلى {phone_number}')
    
    if current_app.debug:
        print(f'📱 WhatsApp Verification OTP لـ {phone_number}: {otp_code}')
    
    return True


def send_email_verification(email, otp_code, supplier_name):
    """
    إرسال OTP للتحقق عبر البريد الإلكتروني
    """
    # TODO: تكامل مع Flask-Mail
    current_app.logger.info(f'[Email] إرسال OTP للتحقق {otp_code} إلى {email}')
    
    if current_app.debug:
        print(f'✉️ Email Verification OTP لـ {email}: {otp_code}')
    
    return True


# ============================================================
# معالج الأخطاء
# ============================================================

@bp.errorhandler(400)
def bad_request_error(error):
    """معالج خطأ 400"""
    if request.is_json:
        return jsonify({'success': False, 'message': 'طلب غير صالح'}), 400
    flash('طلب غير صالح', 'danger')
    return redirect(url_for('auth_register.register_page'))


@bp.errorhandler(500)
def internal_error(error):
    """معالج خطأ 500"""
    if request.is_json:
        return jsonify({'success': False, 'message': 'حدث خطأ داخلي في الخادم'}), 500
    flash('حدث خطأ داخلي في الخادم. يرجى المحاولة مرة أخرى.', 'danger')
    return redirect(url_for('auth_register.register_page'))
