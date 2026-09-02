# -*- coding: utf-8 -*-
# apps/suppliers_auth_portal/routes.py

"""
مسارات المصادقة والتحكم في بوابة الموردين وموظفيهم
يعتمد على النماذج الموجودة في apps/models وخدمات الـ OTP المستقلة
"""

import logging
import re
import random
import string
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_profile_db import SupplierProfile
from apps.models.wallet_db import SupplierWallet
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.product_supplier_map import ProductSupplierMapping

# استيراد خدمة الـ OTP المستقلة التي أنشأناها
from apps.suppliers_auth_portal.otp_service import SupplierOTPService

# إعداد التسجيل
logger = logging.getLogger(__name__)

# إنشاء Blueprint الأساسي
suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/suppliers'
)


# ============================================================
# دوال مساعدة (Helper Functions)
# ============================================================

def validate_phone(phone):
    """التحقق من صحة رقم الهاتف"""
    if not phone:
        return None
    clean_phone = re.sub(r'[^0-9]', '', str(phone))
    if len(clean_phone) >= 7:
        return clean_phone[-9:]  # آخر 9 أرقام
    return None

def validate_email(email):
    """التحقق من صحة البريد الإلكتروني"""
    if not email:
        return None
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_regex, email):
        return email.lower()
    return None

def validate_username(username):
    """التحقق من صحة اسم المستخدم"""
    if not username:
        return None
    if re.match(r'^[a-zA-Z0-9_\u0600-\u06FF]{3,30}$', username):
        return username
    return None

def mask_phone(phone):
    """إخفاء أرقام الهاتف"""
    if not phone or len(phone) <= 4:
        return phone
    return f"{phone[:2]}****{phone[-2:]}"

def mask_email(email):
    """إخفاء البريد الإلكتروني"""
    if not email or '@' not in email:
        return email
    local, domain = email.split('@')
    if len(local) <= 2:
        return f"{local[0]}*@{domain}"
    return f"{local[0]}***{local[-1]}@{domain}"

def find_user(identifier):
    """البحث عن مستخدم (مورد أو موظف) حسب المعرف (البريد، الهاتف، أو اسم المستخدم)"""
    supplier = None
    
    email = validate_email(identifier)
    if email:
        supplier = Supplier.query.filter_by(email=email).first()
    
    phone = validate_phone(identifier)
    if not supplier and phone:
        supplier = Supplier.query.filter_by(phone=phone).first()
        if not supplier and hasattr(Supplier, 'search_phone'):
            supplier = Supplier.query.filter_by(search_phone=phone).first()
    
    username = validate_username(identifier)
    if not supplier and username:
        supplier = Supplier.query.filter_by(username=username).first()
    
    if not supplier:
        supplier = Supplier.query.filter(
            (Supplier.username == identifier) | 
            (Supplier.email == identifier) | 
            (Supplier.phone == identifier)
        ).first()
    
    if supplier:
        return supplier, 'supplier'
    
    employee = None
    if email:
        employee = SupplierStaff.query.filter_by(email=email).first()
    if not employee and phone:
        employee = SupplierStaff.query.filter_by(phone=phone).first()
    if not employee and username:
        employee = SupplierStaff.query.filter_by(username=username).first()
        
    if not employee:
        employee = SupplierStaff.query.filter(
            (SupplierStaff.username == identifier) | 
            (SupplierStaff.email == identifier) | 
            (SupplierStaff.phone == identifier)
        ).first()
    
    if employee:
        return employee, 'employee'
    
    return None, None


# ============================================================
# مسارات المصادقة (Authentication Routes)
# ============================================================

@suppliers_auth_bp.route('/login', methods=['GET'])
def login_page():
    """صفحة تسجيل الدخول"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('suppliers_auth_bp.dashboard'))
        return render_template('suppliers_auth_portal/login.html', page_title='تسجيل الدخول')
    except Exception as e:
        logger.error(f"❌ خطأ فادح أثناء عرض صفحة تسجيل الدخول: {str(e)}", exc_info=True)
        return f"Internal Server Error: {str(e)}", 500


@suppliers_auth_bp.route('/login', methods=['POST'])
def login():
    """معالجة تسجيل الدخول (JSON)"""
    try:
        data = request.get_json(silent=True) or request.form
        if not data:
            return jsonify({'success': False, 'message': 'بيانات غير صالحة'}), 400

        identifier = str(data.get('identifier', '')).strip()
        password = str(data.get('password', ''))
        user_type = str(data.get('user_type', 'supplier'))
        remember_me = bool(data.get('remember_me', False))

        if not identifier or not password:
            return jsonify({'success': False, 'message': 'يرجى إدخال رقم الهاتف أو المعرف وكلمة المرور'}), 400

        user, found_type = find_user(identifier)
        
        if not user:
            return jsonify({'success': False, 'message': 'بيانات الدخول أو كلمة المرور غير صحيحة'}), 401

        if user_type == 'supplier' and found_type != 'supplier':
            return jsonify({'success': False, 'message': 'هذا الحساب ليس حساب مورد'}), 403
        
        if user_type == 'employee' and found_type != 'employee':
            return jsonify({'success': False, 'message': 'هذا الحساب ليس حساب موظف مورد'}), 403

        password_valid = False
        if hasattr(user, 'check_password'):
            password_valid = user.check_password(password)
        elif hasattr(user, 'password_hash'):
            from werkzeug.security import check_password_hash
            password_valid = check_password_hash(user.password_hash, password)

        if not password_valid:
            return jsonify({'success': False, 'message': 'بيانات الدخول أو كلمة المرور غير صحيحة'}), 401

        if hasattr(user, 'is_active') and not user.is_active:
            return jsonify({'success': False, 'message': 'الحساب غير نشط. يرجى التواصل مع الدعم الفني.'}), 403

        login_user(user, remember=remember_me)
        session['user_type'] = found_type
        session['login_time'] = datetime.now().isoformat()
        
        if hasattr(user, 'last_login'):
            user.last_login = datetime.now()
            db.session.commit()

        return jsonify({
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'redirect_url': url_for('suppliers_auth_bp.dashboard')
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ غير متوقع أثناء تسجيل الدخول: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'حدث خطأ داخلي في الخادم: {str(e)}'}), 500


@suppliers_auth_bp.route('/register', methods=['GET'])
def register_page():
    """صفحة تسجيل مورد جديد برقم الهاتف فقط"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('suppliers_auth_bp.dashboard'))
        return render_template('suppliers_auth_portal/register.html', page_title='اشتراك مورد جديد برقم الهاتف')
    except Exception as e:
        logger.error(f"❌ خطأ في عرض صفحة التسجيل: {str(e)}", exc_info=True)
        return f"Internal Server Error: {str(e)}", 500


@suppliers_auth_bp.route('/check-availability', methods=['POST'])
def check_availability():
    """التحقق اللحظي من قاعدة البيانات لتوفر (رقم الهاتف)"""
    try:
        data = request.get_json(silent=True) or {}
        field = data.get('field')
        value = str(data.get('value', '')).strip()

        if not field or not value:
            return jsonify({'available': True})

        if field == 'phone':
            valid_val = validate_phone(value)
            if not valid_val:
                return jsonify({'available': False, 'message': 'رقم الهاتف غير صالح'})
            exists = Supplier.query.filter((Supplier.phone == valid_val) | (Supplier.search_phone == valid_val)).first() or \
                     SupplierStaff.query.filter_by(phone=valid_val).first()
        else:
            return jsonify({'available': True})

        return jsonify({'available': exists is None})
    except Exception as e:
        logger.error(f"❌ خطأ في التحقق اللحظي: {str(e)}", exc_info=True)
        return jsonify({'available': True}), 500


@suppliers_auth_bp.route('/register', methods=['POST'])
def register():
    """معالجة تسجيل مورد جديد برقم الهاتف وكلمة المرور فقط وتفعيل المحفظة تلقائياً"""
    try:
        data = request.get_json(silent=True) or request.form
        if not data:
            return jsonify({'success': False, 'message': 'بيانات غير صالحة'}), 400

        phone = str(data.get('phone', '')).strip()
        password = str(data.get('password', ''))
        confirm_password = str(data.get('confirm_password', ''))

        if not phone or not password or not confirm_password:
            return jsonify({'success': False, 'message': 'رقم الهاتف وكلمة المرور وتأكيدها حقول أساسية مطلوبة'}), 400

        if password != confirm_password:
            return jsonify({'success': False, 'message': 'كلمتا المرور غير متطابقتين'}), 400

        if len(password) < 8:
            return jsonify({'success': False, 'message': 'كلمة المرور يجب أن تكون 8 أحرف على الأقل'}), 400

        valid_phone = validate_phone(phone)
        if not valid_phone:
            return jsonify({'success': False, 'message': 'رقم الهاتف المدخل غير صالح'}), 400

        if Supplier.query.filter_by(phone=valid_phone).first() or Supplier.query.filter_by(search_phone=valid_phone).first():
            return jsonify({'success': False, 'message': 'رقم الهاتف مستخدم بالفعل'}), 409

        random_suffix = ''.join(random.choices(string.digits, k=4))
        generated_username = f"sup_{valid_phone}_{random_suffix}"
        default_display_name = f"مورد رقم {valid_phone}"

        new_supplier = Supplier(
            username=generated_username,
            phone=valid_phone,
            search_phone=valid_phone,
            owner_name=default_display_name,
            trade_name=default_display_name,
            store_name=default_display_name,
            status='active',
            rank='bronze'
        )
        
        if hasattr(new_supplier, 'set_password'):
            new_supplier.set_password(password)
        else:
            from werkzeug.security import generate_password_hash
            new_supplier.password_hash = generate_password_hash(password)

        db.session.add(new_supplier)
        db.session.flush()

        # إنشاء ملف شخصي فارغ يتوافق مع هيكل النموذج (بدون تمرير حقول خاطئة مثل full_address)
        profile = SupplierProfile(
            supplier_id=new_supplier.id
        )
        db.session.add(profile)

        wallet = SupplierWallet(
            supplier_id=new_supplier.id,
            currency='YER',
            is_active=True,
            balance=0.0,
            pending_balance=0.0,
            total_earned=0.0,
            total_withdrawn=0.0
        )
        db.session.add(wallet)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'تم إنشاء حساب المورد والمحفظة المالية الذكية بنجاح',
            'redirect_url': url_for('suppliers_auth_bp.login_page')
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ أثناء التسجيل: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'خطأ في الخادم: {str(e)}'}), 500


@suppliers_auth_bp.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    """صفحة استعادة كلمة المرور"""
    try:
        return render_template('suppliers_auth_portal/forgot_password.html', page_title='استعادة كلمة المرور')
    except Exception as e:
        logger.error(f"❌ خطأ في صفحة الاستعادة: {str(e)}", exc_info=True)
        return f"Internal Server Error: {str(e)}", 500


@suppliers_auth_bp.route('/forgot-password/request-otp', methods=['POST'])
@suppliers_auth_bp.route('/supplier/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """طلب رمز التحقق OTP عبر الواتساب باستخدام خدمة SupplierOTPService المستقلة"""
    try:
        data = request.get_json(silent=True) or request.form
        identifier = str(data.get('identifier', '')).strip()
        if not identifier:
            return jsonify({'success': False, 'message': 'يرجى إدخال رقم الهاتف'}), 400

        user, user_type = find_user(identifier)
        if not user:
            return jsonify({'success': False, 'message': 'الحساب غير موجود'}), 404

        target_phone = getattr(user, 'phone', None)
        if not target_phone:
            return jsonify({'success': False, 'message': 'لا يوجد رقم هاتف مسجل لهذا الحساب لإرسال رمز الواتساب'}), 400

        result = SupplierOTPService.generate_and_send_otp(
            identifier=target_phone,
            target_id=user.id,
            target_type=user_type,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        if not result.get("success"):
            return jsonify({'success': False, 'message': result.get("error", 'فشل إرسال رمز التحقق عبر واتساب')}), 500

        session['reset_otp_data'] = {
            'identifier': identifier,
            'user_type': user_type,
            'user_id': user.id,
            'phone': target_phone
        }

        return jsonify({
            'success': True,
            'otp_sent': True,
            'message': 'تم إرسال رمز التحقق بنجاح إلى رقم الواتساب المرتبط بالحساب',
            'data': {'masked_phone': mask_phone(target_phone)}
        })
    except Exception as e:
        logger.error(f"❌ خطأ OTP واتساب: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@suppliers_auth_bp.route('/reset-password', methods=['POST'])
@suppliers_auth_bp.route('/supplier/reset-password', methods=['POST'])
def reset_password():
    """التحقق من رمز OTP وتحديث كلمة المرور للمورد أو الموظف"""
    try:
        data = request.get_json(silent=True) or request.form
        if not data:
            return jsonify({'success': False, 'message': 'بيانات غير صالحة'}), 400

        otp_code = str(data.get('otp_code', '')).strip()
        new_password = str(data.get('new_password', ''))
        confirm_password = str(data.get('confirm_password', ''))

        if not all([otp_code, new_password, confirm_password]):
            return jsonify({'success': False, 'message': 'جميع الحقول مطلوبة'}), 400

        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'كلمتا المرور غير متطابقتين'}), 400

        if len(new_password) < 8:
            return jsonify({'success': False, 'message': 'كلمة المرور الجديدة يجب ألا تقل عن 8 أحرف'}), 400

        stored_session_data = session.get('reset_otp_data')
        if not stored_session_data:
            return jsonify({'success': False, 'message': 'انتهت صلاحية الجلسة أو لم يتم طلب رمز تحقق'}), 400

        target_phone = stored_session_data.get('phone')

        verification_result = SupplierOTPService.verify_otp(target_phone, otp_code)
        if not verification_result.get('success'):
            return jsonify({
                'success': False, 
                'message': verification_result.get('message', 'رمز التحقق غير صحيح أو انتهت صلاحيته')
            }), 400

        user_id = stored_session_data['user_id']
        u_type = stored_session_data['user_type']

        if u_type == 'supplier':
            user = Supplier.query.get(user_id)
        else:
            user = SupplierStaff.query.get(user_id)

        if not user:
            return jsonify({'success': False, 'message': 'المستخدم غير موجود'}), 404

        if hasattr(user, 'set_password'):
            user.set_password(new_password)
        else:
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash(new_password)

        db.session.commit()
        session.pop('reset_otp_data', None)

        return jsonify({
            'success': True,
            'message': 'تم تحديث كلمة المرور بنجاح، يمكنك تسجيل الدخول الآن',
            'redirect_url': url_for('suppliers_auth_bp.login_page')
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ أثناء إعادة تعيين كلمة المرور: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'حدث خطأ في الخادم: {str(e)}'}), 500


@suppliers_auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """تسجيل الخروج"""
    logout_user()
    session.clear()
    return redirect(url_for('suppliers_auth_bp.login_page'))


@suppliers_auth_bp.route('/dashboard')
@login_required
def dashboard():
    """عرض لوحة التحكم الخاصة بالمورد مباشرة"""
    try:
        supplier = current_user if session.get('user_type') == 'supplier' else getattr(current_user, 'supplier', None)
        profile = SupplierProfile.query.filter_by(supplier_id=supplier.id).first() if supplier else None
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first() if supplier else None
        balance = wallet.balance if wallet else 0.0
        products_count = ProductSupplierMapping.query.filter_by(supplier_id=supplier.id).count() if supplier else 0
        staff_count = SupplierStaff.query.filter_by(supplier_id=supplier.id).count() if supplier else 0

        return render_template(
            'suppliers/dashboard.html',
            page_title='لوحة تحكم المورد | محجوب أونلاين',
            supplier=supplier,
            profile=profile,
            wallet=wallet,
            balance=balance,
            products_count=products_count,
            staff_count=staff_count
        )
    except Exception as e:
        logger.error(f"❌ خطأ أثناء عرض لوحة التحكم: {str(e)}", exc_info=True)
        return f"Internal Server Error: {str(e)}", 500


# ============================================================
# سياق القوالب والتكوين
# ============================================================

@suppliers_auth_bp.context_processor
def utility_processor():
    return {
        'csrf_token': lambda: session.get('csrf_token', ''),
        'get_user_type': lambda: session.get('user_type', ''),
        'is_authenticated': current_user.is_authenticated,
        'now': datetime.now
    }

def init_app(app):
    """تهيئة التطبيق"""
    if not app.blueprints.get('suppliers_auth_bp'):
        app.register_blueprint(suppliers_auth_bp)
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('suppliers_auth_bp.dashboard'))
        return redirect(url_for('suppliers_auth_bp.login_page'))
    
    logger.info("✅ تم تهيئة بوابة مصادقة الموردين بنجاح مع ربط خدمة الـ OTP المستقلة")
    return app
