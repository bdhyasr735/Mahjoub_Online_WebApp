"""
سجل المصادقة والتحكم في بوابة الموردين وموظفيهم
suppliers_auth_portal/registry.py

يوفر هذا الملف:
- تسجيل Blueprint للمصادقة
- تكوين المسارات (routes)
- ربط القوالب والوظائف المساعدة
- إعداد middleware للأمان
- تكامل مع نظام الحوكمة
"""

import logging
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import re
import random
import string

# إعداد التسجيل
logger = logging.getLogger(__name__)

# إنشاء Blueprint
suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp',
    __name__,
    template_folder='templates/suppliers_auth_portal',
    static_folder='static/suppliers_auth_portal',
    url_prefix='/suppliers'
)

# ============================================================
# دوال مساعدة (Helper Functions)
# ============================================================

def validate_phone(phone):
    """التحقق من صحة رقم الهاتف اليمني"""
    # إزالة أي أحرف غير رقمية
    clean_phone = re.sub(r'[^0-9]', '', phone)
    # التحقق: يبدأ بـ 7 أو 77 أو 70 أو 71 أو 73 أو 77 أو 78
    if re.match(r'^(7|77|70|71|73|78)[0-9]{7,8}$', clean_phone):
        return clean_phone
    return None

def validate_email(email):
    """التحقق من صحة البريد الإلكتروني"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_regex, email):
        return email.lower()
    return None

def validate_username(username):
    """التحقق من صحة اسم المستخدم"""
    # 3-30 حرفاً، حروف عربية/إنجليزية، أرقام، _
    if re.match(r'^[a-zA-Z0-9_\u0600-\u06FF]{3,30}$', username):
        return username
    return None

def generate_otp():
    """توليد رمز تحقق عشوائي مكون من 6 أرقام"""
    return ''.join(random.choices(string.digits, k=6))

def mask_phone(phone):
    """إخفاء أرقام الهاتف مع إظهار الأرقام الأولى والأخيرة"""
    if len(phone) <= 4:
        return phone
    return f"{phone[:2]}****{phone[-2:]}"

def mask_email(email):
    """إخفاء البريد الإلكتروني مع إظهار الحرف الأول والآخر"""
    if '@' not in email:
        return email
    local, domain = email.split('@')
    if len(local) <= 2:
        return f"{local[0]}*@{domain}"
    return f"{local[0]}***{local[-1]}@{domain}"

# ============================================================
# مسارات المصادقة (Authentication Routes)
# ============================================================

@suppliers_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    صفحة تسجيل الدخول للموردين وموظفيهم
    يدعم نوعين من المستخدمين: supplier و employee
    """
    # إذا كان المستخدم مسجلاً بالفعل، إعادة توجيه إلى لوحة التحكم
    if current_user.is_authenticated:
        return redirect(url_for('suppliers_auth_bp.dashboard'))

    if request.method == 'GET':
        return render_template('login.html', page_title='تسجيل الدخول')

    # معالجة POST
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'بيانات غير صالحة'
            }), 400

        identifier = data.get('identifier', '').strip()
        password = data.get('password', '')
        user_type = data.get('user_type', 'supplier')
        remember_me = data.get('remember_me', False)
        csrf_token = data.get('csrf_token', '')

        # التحقق من CSRF
        session_csrf = session.get('csrf_token')
        if not csrf_token or csrf_token != session_csrf:
            logger.warning(f"CSRF validation failed for identifier: {identifier}")
            return jsonify({
                'success': False,
                'message': 'طلب غير آمن. يرجى تحديث الصفحة والمحاولة مرة أخرى.'
            }), 403

        # البحث عن المستخدم
        user = None
        from models import Supplier, Employee  # افتراضي

        # محاولة البحث باستخدام البريد الإلكتروني
        if validate_email(identifier):
            if user_type == 'supplier':
                user = Supplier.query.filter_by(email=identifier).first()
            else:
                user = Employee.query.filter_by(email=identifier).first()

        # محاولة البحث باستخدام رقم الهاتف
        if not user:
            phone = validate_phone(identifier)
            if phone:
                if user_type == 'supplier':
                    user = Supplier.query.filter_by(phone=phone).first()
                else:
                    user = Employee.query.filter_by(phone=phone).first()

        # محاولة البحث باستخدام اسم المستخدم
        if not user and validate_username(identifier):
            if user_type == 'supplier':
                user = Supplier.query.filter_by(username=identifier).first()
            else:
                user = Employee.query.filter_by(username=identifier).first()

        # التحقق من وجود المستخدم وكلمة المرور
        if not user or not check_password_hash(user.password_hash, password):
            logger.warning(f"Failed login attempt for: {identifier} (type: {user_type})")
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'
            }), 401

        # التحقق من حالة المستخدم
        if hasattr(user, 'is_active') and not user.is_active:
            return jsonify({
                'success': False,
                'message': 'الحساب غير نشط. يرجى التواصل مع الدعم الفني.'
            }), 403

        # التحقق من صلاحية نوع المستخدم
        if user_type == 'supplier' and not isinstance(user, Supplier):
            return jsonify({
                'success': False,
                'message': 'هذا الحساب ليس حساب مورد'
            }), 403

        if user_type == 'employee' and not isinstance(user, Employee):
            return jsonify({
                'success': False,
                'message': 'هذا الحساب ليس حساب موظف مورد'
            }), 403

        # تسجيل الدخول
        login_user(user, remember=remember_me)
        session['user_type'] = user_type
        session['login_time'] = datetime.now().isoformat()

        logger.info(f"Successful login: {user.username} ({user_type})")

        # إعادة التوجيه إلى لوحة التحكم
        return jsonify({
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'redirect_url': url_for('suppliers_auth_bp.dashboard')
        })

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'حدث خطأ أثناء محاولة تسجيل الدخول'
        }), 500


@suppliers_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    صفحة تسجيل مورد جديد
    إنشاء حساب مورد مع لوحة تحكم مجانية
    """
    if current_user.is_authenticated:
        return redirect(url_for('suppliers_auth_bp.dashboard'))

    if request.method == 'GET':
        return render_template('register.html', page_title='اشتراك مورد جديد')

    # معالجة POST
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'بيانات غير صالحة'
            }), 400

        # استخراج البيانات
        company_name = data.get('company_name', '').strip()
        business_type = data.get('business_type', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        csrf_token = data.get('csrf_token', '')

        # التحقق من CSRF
        session_csrf = session.get('csrf_token')
        if not csrf_token or csrf_token != session_csrf:
            return jsonify({
                'success': False,
                'message': 'طلب غير آمن. يرجى تحديث الصفحة والمحاولة مرة أخرى.'
            }), 403

        # التحقق من الحقول المطلوبة
        if not all([company_name, business_type, email, phone, username, password]):
            return jsonify({
                'success': False,
                'message': 'جميع الحقول مطلوبة'
            }), 400

        # التحقق من تطابق كلمة المرور
        if password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'كلمتا المرور غير متطابقتين'
            }), 400

        # التحقق من قوة كلمة المرور
        if len(password) < 8:
            return jsonify({
                'success': False,
                'message': 'كلمة المرور يجب أن تحتوي على 8 أحرف على الأقل'
            }), 400

        # التحقق من البريد الإلكتروني
        valid_email = validate_email(email)
        if not valid_email:
            return jsonify({
                'success': False,
                'message': 'البريد الإلكتروني غير صالح'
            }), 400

        # التحقق من رقم الهاتف
        valid_phone = validate_phone(phone)
        if not valid_phone:
            return jsonify({
                'success': False,
                'message': 'رقم الهاتف غير صالح. يجب أن يبدأ بـ 7 أو 77 أو 70 أو 71 أو 73 أو 78'
            }), 400

        # التحقق من اسم المستخدم
        valid_username = validate_username(username)
        if not valid_username:
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم غير صالح. يجب أن يحتوي على 3-30 حرفاً (حروف، أرقام، _)'
            }), 400

        from models import Supplier, db

        # التحقق من عدم وجود بيانات مكررة
        if Supplier.query.filter_by(email=valid_email).first():
            return jsonify({
                'success': False,
                'message': 'البريد الإلكتروني مستخدم بالفعل'
            }), 409

        if Supplier.query.filter_by(phone=valid_phone).first():
            return jsonify({
                'success': False,
                'message': 'رقم الهاتف مستخدم بالفعل'
            }), 409

        if Supplier.query.filter_by(username=valid_username).first():
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم مستخدم بالفعل'
            }), 409

        # إنشاء حساب المورد الجديد
        new_supplier = Supplier(
            company_name=company_name,
            business_type=business_type,
            email=valid_email,
            phone=valid_phone,
            username=valid_username,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
            is_active=True,
            is_verified=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.session.add(new_supplier)
        db.session.commit()

        logger.info(f"New supplier registered: {valid_username} ({valid_email})")

        return jsonify({
            'success': True,
            'message': 'تم إنشاء حساب المورد بنجاح. يمكنك الآن تسجيل الدخول.',
            'redirect_url': url_for('suppliers_auth_bp.login')
        })

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'حدث خطأ أثناء إنشاء الحساب'
        }), 500


@suppliers_auth_bp.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    """صفحة استعادة كلمة المرور"""
    return render_template('forgot_password.html', page_title='استعادة كلمة المرور')


@suppliers_auth_bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """
    طلب رمز التحقق (OTP) لاستعادة كلمة المرور
    التحقق من الهوية وإرسال OTP عبر SMS أو البريد الإلكتروني
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'بيانات غير صالحة'
            }), 400

        identifier = data.get('identifier', '').strip()
        csrf_token = data.get('csrf_token', '')

        # التحقق من CSRF
        session_csrf = session.get('csrf_token')
        if not csrf_token or csrf_token != session_csrf:
            return jsonify({
                'success': False,
                'message': 'طلب غير آمن'
            }), 403

        if not identifier:
            return jsonify({
                'success': False,
                'message': 'يرجى إدخال اسم المستخدم أو رقم الهاتف أو البريد الإلكتروني'
            }), 400

        from models import Supplier, Employee, db

        # البحث عن المستخدم
        user = None
        user_type = None
        masked_target = identifier

        # البحث في الموردين
        if validate_email(identifier):
            user = Supplier.query.filter_by(email=identifier).first()
            if user:
                user_type = 'supplier'
                masked_target = mask_email(identifier)
        if not user:
            phone = validate_phone(identifier)
            if phone:
                user = Supplier.query.filter_by(phone=phone).first()
                if user:
                    user_type = 'supplier'
                    masked_target = mask_phone(phone)

        # البحث في الموظفين
        if not user:
            if validate_email(identifier):
                user = Employee.query.filter_by(email=identifier).first()
                if user:
                    user_type = 'employee'
                    masked_target = mask_email(identifier)
        if not user:
            phone = validate_phone(identifier)
            if phone:
                user = Employee.query.filter_by(phone=phone).first()
                if user:
                    user_type = 'employee'
                    masked_target = mask_phone(phone)

        # البحث باسم المستخدم
        if not user and validate_username(identifier):
            user = Supplier.query.filter_by(username=identifier).first()
            if user:
                user_type = 'supplier'
            else:
                user = Employee.query.filter_by(username=identifier).first()
                if user:
                    user_type = 'employee'

        if not user:
            return jsonify({
                'success': False,
                'message': 'لم يتم العثور على حساب مرتبط بالبيانات المدخلة'
            }), 404

        # توليد OTP
        otp_code = generate_otp()

        # تخزين OTP في الجلسة أو قاعدة البيانات
        session['reset_otp'] = {
            'code': otp_code,
            'identifier': identifier,
            'user_type': user_type,
            'user_id': user.id,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=10)).isoformat()
        }

        # TODO: إرسال OTP عبر SMS (للمرحلة الإنتاجية)
        # في التطوير: نعيد OTP في الاستجابة
        # في الإنتاج: يجب إرسال OTP عبر SMS/البريد الإلكتروني فقط

        logger.info(f"OTP generated for user: {user.username} (type: {user_type})")

        # إرجاع النجاح مع OTP للتطوير فقط
        return jsonify({
            'success': True,
            'otp_sent': True,
            'message': 'تم إرسال رمز التحقق بنجاح',
            'data': {
                'masked_phone': masked_target,
                '_dev_otp': otp_code  # للتطوير فقط - يجب إزالته في الإنتاج
            }
        })

    except Exception as e:
        logger.error(f"Request OTP error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'حدث خطأ أثناء طلب رمز التحقق'
        }), 500


@suppliers_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """تحديث كلمة المرور بعد التحقق من OTP"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'بيانات غير صالحة'
            }), 400

        identifier = data.get('identifier', '').strip()
        otp_code = data.get('otp_code', '').strip()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        csrf_token = data.get('csrf_token', '')

        # التحقق من CSRF
        session_csrf = session.get('csrf_token')
        if not csrf_token or csrf_token != session_csrf:
            return jsonify({
                'success': False,
                'message': 'طلب غير آمن'
            }), 403

        # التحقق من الحقول المطلوبة
        if not all([identifier, otp_code, new_password, confirm_password]):
            return jsonify({
                'success': False,
                'message': 'جميع الحقول مطلوبة'
            }), 400

        # التحقق من تطابق كلمة المرور
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'كلمتا المرور غير متطابقتين'
            }), 400

        # التحقق من قوة كلمة المرور
        if len(new_password) < 8:
            return jsonify({
                'success': False,
                'message': 'كلمة المرور يجب أن تحتوي على 8 أحرف على الأقل'
            }), 400

        # التحقق من OTP
        reset_data = session.get('reset_otp')
        if not reset_data:
            return jsonify({
                'success': False,
                'message': 'لم يتم طلب رمز تحقق. يرجى بدء العملية مرة أخرى.'
            }), 400

        # التحقق من صلاحية OTP
        expires_at = datetime.fromisoformat(reset_data['expires_at'])
        if datetime.now() > expires_at:
            session.pop('reset_otp', None)
            return jsonify({
                'success': False,
                'message': 'انتهت صلاحية رمز التحقق. يرجى طلب رمز جديد.'
            }), 400

        # التحقق من تطابق OTP
        if reset_data['code'] != otp_code:
            return jsonify({
                'success': False,
                'message': 'رمز التحقق غير صحيح'
            }), 400

        # التحقق من تطابق المعرف
        if reset_data['identifier'] != identifier:
            return jsonify({
                'success': False,
                'message': 'تعارض في بيانات المستخدم'
            }), 400

        from models import Supplier, Employee, db

        # تحديث كلمة المرور
        user_type = reset_data['user_type']
        user_id = reset_data['user_id']

        if user_type == 'supplier':
            user = Supplier.query.get(user_id)
        else:
            user = Employee.query.get(user_id)

        if not user:
            return jsonify({
                'success': False,
                'message': 'المستخدم غير موجود'
            }), 404

        # تحديث كلمة المرور
        user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        user.updated_at = datetime.now()

        db.session.commit()

        # حذف OTP من الجلسة
        session.pop('reset_otp', None)

        logger.info(f"Password reset successful for user: {user.username}")

        return jsonify({
            'success': True,
            'message': 'تم تحديث كلمة المرور بنجاح',
            'redirect_url': url_for('suppliers_auth_bp.login')
        })

    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'حدث خطأ أثناء تحديث كلمة المرور'
        }), 500


@suppliers_auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """تسجيل الخروج من المنصة"""
    logout_user()
    session.clear()
    return redirect(url_for('suppliers_auth_bp.login'))


@suppliers_auth_bp.route('/dashboard')
@login_required
def dashboard():
    """
    لوحة التحكم الرئيسية للموردين وموظفيهم
    يتم توجيه المستخدم هنا بعد تسجيل الدخول الناجح
    """
    user_type = session.get('user_type', 'supplier')

    # التحقق من نوع المستخدم
    if user_type == 'supplier':
        # عرض لوحة تحكم المورد
        return render_template(
            'dashboard/supplier_dashboard.html',
            page_title='لوحة تحكم المورد',
            user=current_user
        )
    else:
        # عرض لوحة تحكم موظف المورد
        return render_template(
            'dashboard/employee_dashboard.html',
            page_title='لوحة تحكم موظف المورد',
            user=current_user
        )


# ============================================================
# Middleware وتكوين الأمان
# ============================================================

@suppliers_auth_bp.before_request
def before_request():
    """إعدادات ما قبل كل طلب"""
    # تحديث CSRF token لكل طلب GET
    if request.method == 'GET':
        if 'csrf_token' not in session:
            session['csrf_token'] = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    # التحقق من الجلسة المنتهية
    if current_user.is_authenticated:
        # التحقق من انتهاء الجلسة (اختياري)
        pass


@suppliers_auth_bp.after_request
def after_request(response):
    """إعدادات ما بعد كل طلب"""
    # إضافة رؤوس الأمان
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

    return response


# ============================================================
# سياق القوالب (Template Context)
# ============================================================

@suppliers_auth_bp.context_processor
def utility_processor():
    """إضافة دوال مساعدة إلى جميع القوالب"""
    def get_csrf_token():
        return session.get('csrf_token', '')

    def is_authenticated():
        return current_user.is_authenticated

    return {
        'csrf_token': get_csrf_token,
        'is_authenticated': is_authenticated,
        'now': datetime.now,
        'version': '2.0.0'
    }


# ============================================================
# Error Handlers
# ============================================================

@suppliers_auth_bp.errorhandler(404)
def not_found_error(error):
    """معالجة خطأ 404"""
    return render_template('errors/404.html'), 404


@suppliers_auth_bp.errorhandler(403)
def forbidden_error(error):
    """معالجة خطأ 403"""
    return render_template('errors/403.html'), 403


@suppliers_auth_bp.errorhandler(500)
def internal_error(error):
    """معالجة خطأ 500"""
    logger.error(f"Internal server error: {str(error)}")
    return render_template('errors/500.html'), 500


# ============================================================
# تكوين التطبيق - يتم استدعاؤه من __init__.py
# ============================================================

def init_app(app):
    """
    تهيئة تطبيق Flask مع Blueprint المصادقة
    يجب استدعاؤها من ملف __init__.py الرئيسي
    """
    app.register_blueprint(suppliers_auth_bp)

    # إضافة مسار تسجيل الدخول الافتراضي
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('suppliers_auth_bp.dashboard'))
        return redirect(url_for('suppliers_auth_bp.login'))

    logger.info("Suppliers Auth Portal initialized successfully")

    return app


# ============================================================
# نموذج المستخدمين (Models) - يجب وضعها في ملف منفصل
# ============================================================

# هذه النماذج توضيحية - يجب نقلها إلى models.py
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Supplier(db.Model, UserMixin):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    business_type = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

class Employee(db.Model, UserMixin):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)
"""

if __name__ == '__main__':
    print("=" * 60)
    print("🔐 Suppliers Auth Portal Registry")
    print("=" * 60)
    print(f"📌 Blueprint Name: {suppliers_auth_bp.name}")
    print(f"📌 URL Prefix: {suppliers_auth_bp.url_prefix}")
    print(f"📌 Template Folder: {suppliers_auth_bp.template_folder}")
    print("=" * 60)
    print("✅ تم تحميل سجل المصادقة بنجاح")
