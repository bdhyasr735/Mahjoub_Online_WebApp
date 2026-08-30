# apps/suppliers_auth_portal/routes.py

"""
مسارات المصادقة والتحكم في بوابة الموردين وموظفيهم
يعتمد على النماذج الموجودة في apps/models
"""

import logging
import re
import random
import string
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_profile_db import SupplierProfile
from apps.models.wallet_db import SupplierWallet
from apps.models.supplier_staff_db import SupplierStaff, SupplierStaffRole
from apps.models.supplier_invitation_db import SupplierInvitation
from apps.models.product_supplier_map import ProductSupplierMapping

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

def generate_otp():
    """توليد رمز تحقق عشوائي مكون من 6 أرقام"""
    return ''.join(random.choices(string.digits, k=6))

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
    """البحث عن مستخدم (مورد أو موظف) حسب المعرف"""
    # البحث في الموردين
    supplier = None
    
    # بحث بالبريد الإلكتروني
    email = validate_email(identifier)
    if email:
        supplier = Supplier.query.filter_by(email=email).first()
    
    # بحث برقم الهاتف
    if not supplier:
        phone = validate_phone(identifier)
        if phone:
            supplier = Supplier.query.filter_by(search_phone=phone).first()
    
    # بحث باسم المستخدم
    if not supplier:
        username = validate_username(identifier)
        if username:
            supplier = Supplier.query.filter_by(username=username).first()
    
    if supplier:
        return supplier, 'supplier'
    
    # البحث في الموظفين
    employee = None
    
    # بحث بالبريد الإلكتروني
    if email:
        employee = SupplierStaff.query.filter_by(email=email).first()
    
    # بحث برقم الهاتف
    if not employee and phone:
        employee = SupplierStaff.query.filter_by(phone=phone).first()
    
    # بحث باسم المستخدم
    if not employee and username:
        employee = SupplierStaff.query.filter_by(username=username).first()
    
    if employee:
        return employee, 'employee'
    
    return None, None


# ============================================================
# مسارات المصادقة (Authentication Routes)
# ============================================================

@suppliers_auth_bp.route('/login', methods=['GET'])
def login_page():
    """صفحة تسجيل الدخول"""
    if current_user.is_authenticated:
        # التحقق من نوع المستخدم
        if hasattr(current_user, 'supplier_id'):  # موظف
            return redirect(url_for('suppliers_auth_bp.dashboard'))
        else:  # مورد
            return redirect(url_for('suppliers_auth_bp.dashboard'))
    
    return render_template('login.html', page_title='تسجيل الدخول')


@suppliers_auth_bp.route('/login', methods=['POST'])
def login():
    """معالجة تسجيل الدخول (JSON)"""
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

        if not identifier or not password:
            return jsonify({
                'success': False,
                'message': 'يرجى إدخال اسم المستخدم وكلمة المرور'
            }), 400

        # البحث عن المستخدم
        user, found_type = find_user(identifier)
        
        if not user:
            logger.warning(f"⚠️ محاولة دخول فاشلة: {identifier}")
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'
            }), 401

        # التحقق من نوع المستخدم المطلوب
        if user_type == 'supplier' and found_type != 'supplier':
            return jsonify({
                'success': False,
                'message': 'هذا الحساب ليس حساب مورد'
            }), 403
        
        if user_type == 'employee' and found_type != 'employee':
            return jsonify({
                'success': False,
                'message': 'هذا الحساب ليس حساب موظف مورد'
            }), 403

        # التحقق من كلمة المرور
        if not user.check_password(password):
            logger.warning(f"⚠️ كلمة مرور خاطئة: {user.username}")
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'
            }), 401

        # التحقق من حالة المستخدم
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'الحساب غير نشط. يرجى التواصل مع الدعم الفني.'
            }), 403

        # تسجيل الدخول
        login_user(user, remember=remember_me)
        session['user_type'] = found_type
        session['login_time'] = datetime.now().isoformat()
        
        # تحديث آخر تسجيل دخول
        user.last_login = datetime.now()
        db.session.commit()

        logger.info(f"✅ تم تسجيل الدخول: {user.username} ({found_type})")

        return jsonify({
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'redirect_url': url_for('suppliers_auth_bp.dashboard')
        })

    except Exception as e:
        logger.error(f"❌ خطأ في تسجيل الدخول: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'حدث خطأ أثناء محاولة تسجيل الدخول'
        }), 500


@suppliers_auth_bp.route('/register', methods=['GET'])
def register_page():
    """صفحة تسجيل مورد جديد"""
    if current_user.is_authenticated:
        return redirect(url_for('suppliers_auth_bp.dashboard'))
    
    return render_template('register.html', page_title='اشتراك مورد جديد')


@suppliers_auth_bp.route('/register', methods=['POST'])
def register():
    """معالجة تسجيل مورد جديد"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'بيانات غير صالحة'
            }), 400

        # استخراج البيانات
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        owner_name = data.get('owner_name', '').strip()
        trade_name = data.get('trade_name', '').strip()
        store_name = data.get('store_name', '').strip()
        business_type = data.get('business_type', '').strip()
        full_address = data.get('full_address', '').strip()
        city = data.get('city', '').strip()
        district = data.get('district', '').strip()

        # التحقق من الحقول المطلوبة
        required_fields = [username, email, phone, password, confirm_password]
        if not all(required_fields):
            return jsonify({
                'success': False,
                'message': 'جميع الحقول المطلوبة يجب تعبئتها'
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
                'message': 'رقم الهاتف غير صالح'
            }), 400

        # التحقق من اسم المستخدم
        valid_username = validate_username(username)
        if not valid_username:
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم غير صالح (3-30 حرفاً، حروف، أرقام، _)'
            }), 400

        # التحقق من عدم وجود بيانات مكررة
        if Supplier.query.filter_by(email=valid_email).first():
            return jsonify({
                'success': False,
                'message': 'البريد الإلكتروني مستخدم بالفعل'
            }), 409

        if Supplier.query.filter_by(search_phone=valid_phone).first():
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
            username=valid_username,
            email=valid_email,
            phone=phone,  # يتم تشفيره تلقائياً
            owner_name=owner_name or trade_name or store_name,
            trade_name=trade_name,
            store_name=store_name or trade_name,
            status='active',
            rank='bronze'
        )
        new_supplier.set_password(password)

        db.session.add(new_supplier)
        db.session.flush()  # للحصول على ID

        # إنشاء ملف تعريف المورد
        profile = SupplierProfile(
            supplier_id=new_supplier.id,
            full_address=full_address,
            city=city,
            district=district
        )
        db.session.add(profile)

        # إنشاء محفظة المورد (سيتم توليد WEL-963X تلقائياً)
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

        logger.info(f"✅ تم تسجيل مورد جديد: {valid_username} ({valid_email})")

        return jsonify({
            'success': True,
            'message': 'تم إنشاء حساب المورد بنجاح. يمكنك الآن تسجيل الدخول.',
            'redirect_url': url_for('suppliers_auth_bp.login_page')
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ في التسجيل: {str(e)}")
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
    """طلب رمز التحقق (OTP) لاستعادة كلمة المرور"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'بيانات غير صالحة'
            }), 400

        identifier = data.get('identifier', '').strip()

        if not identifier:
            return jsonify({
                'success': False,
                'message': 'يرجى إدخال اسم المستخدم أو رقم الهاتف أو البريد الإلكتروني'
            }), 400

        # البحث عن المستخدم
        user, user_type = find_user(identifier)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'لم يتم العثور على حساب مرتبط بالبيانات المدخلة'
            }), 404

        # تحديد الوجهة المقنعة
        if validate_email(identifier):
            masked_target = mask_email(identifier)
        elif validate_phone(identifier):
            masked_target = mask_phone(validate_phone(identifier))
        else:
            masked_target = identifier

        # توليد OTP
        otp_code = generate_otp()

        # تخزين OTP في الجلسة
        session['reset_otp'] = {
            'code': otp_code,
            'identifier': identifier,
            'user_type': user_type,
            'user_id': user.id,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=10)).isoformat()
        }

        logger.info(f"📱 تم توليد OTP للمستخدم: {user.username} (type: {user_type})")

        # TODO: إرسال OTP عبر SMS/بريد إلكتروني
        # في الإنتاج: استخدم Twilio أو أي خدمة SMS

        return jsonify({
            'success': True,
            'otp_sent': True,
            'message': 'تم إرسال رمز التحقق بنجاح',
            'data': {
                'masked_phone': masked_target,
                '_dev_otp': otp_code  # ⚠️ للتطوير فقط
            }
        })

    except Exception as e:
        logger.error(f"❌ خطأ في طلب OTP: {str(e)}")
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

        # الحصول على المستخدم
        user_type = reset_data['user_type']
        user_id = reset_data['user_id']

        if user_type == 'supplier':
            user = Supplier.query.get(user_id)
        else:
            user = SupplierStaff.query.get(user_id)

        if not user:
            return jsonify({
                'success': False,
                'message': 'المستخدم غير موجود'
            }), 404

        # تحديث كلمة المرور
        user.set_password(new_password)
        db.session.commit()

        # حذف OTP من الجلسة
        session.pop('reset_otp', None)

        logger.info(f"✅ تم تحديث كلمة المرور: {user.username}")

        return jsonify({
            'success': True,
            'message': 'تم تحديث كلمة المرور بنجاح',
            'redirect_url': url_for('suppliers_auth_bp.login_page')
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ في تحديث كلمة المرور: {str(e)}")
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
    return redirect(url_for('suppliers_auth_bp.login_page'))


@suppliers_auth_bp.route('/dashboard')
@login_required
def dashboard():
    """
    🏠 لوحة التحكم الرئيسية
    يتم توجيه المستخدم هنا بعد تسجيل الدخول الناجح
    """
    user_type = session.get('user_type', 'supplier')
    
    if user_type == 'supplier' and hasattr(current_user, 'id'):
        # إحصائيات المورد
        supplier_id = current_user.id
        
        # عدد المنتجات
        products_count = ProductSupplierMapping.query.filter_by(
            supplier_id=supplier_id,
            is_active=True
        ).count()
        
        # رصيد المحفظة
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        balance = wallet.balance if wallet else 0.0
        
        # عدد الموظفين
        staff_count = SupplierStaff.query.filter_by(
            supplier_id=supplier_id,
            is_active=True
        ).count()
        
        # ملف التعريف
        profile = SupplierProfile.query.filter_by(supplier_id=supplier_id).first()
        
        return render_template(
            'dashboard/supplier_dashboard.html',
            page_title='لوحة تحكم المورد',
            user=current_user,
            profile=profile,
            wallet=wallet,
            products_count=products_count,
            staff_count=staff_count,
            balance=balance,
            last_login=session.get('login_time', '')
        )
    
    elif user_type == 'employee':
        # عرض لوحة تحكم موظف المورد
        return render_template(
            'dashboard/employee_dashboard.html',
            page_title='لوحة تحكم موظف المورد',
            user=current_user
        )
    
    return redirect(url_for('suppliers_auth_bp.login_page'))


# ============================================================
# سياق القوالب (Template Context)
# ============================================================

@suppliers_auth_bp.context_processor
def utility_processor():
    """إضافة دوال مساعدة إلى جميع القوالب"""
    def get_csrf_token():
        return session.get('csrf_token', '')
    
    def get_user_type():
        return session.get('user_type', '')
    
    return {
        'csrf_token': get_csrf_token,
        'get_user_type': get_user_type,
        'is_authenticated': current_user.is_authenticated,
        'now': datetime.now
    }


# ============================================================
# تكوين التطبيق
# ============================================================

def init_app(app):
    """تهيئة تطبيق Flask مع Blueprint المصادقة"""
    app.register_blueprint(suppliers_auth_bp)
    
    # المسار الرئيسي
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('suppliers_auth_bp.dashboard'))
        return redirect(url_for('suppliers_auth_bp.login_page'))
    
    logger.info("✅ تم تهيئة بوابة مصادقة الموردين بنجاح")
    return app


# ============================================================
# Debug Info
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🔐 Suppliers Auth Portal - Routes")
    print("=" * 60)
    print(f"📌 Blueprint: {suppliers_auth_bp.name}")
    print(f"📌 URL Prefix: {suppliers_auth_bp.url_prefix}")
    print(f"📌 Template Folder: {suppliers_auth_bp.template_folder}")
    print("=" * 60)
    print("✅ Routes loaded successfully")
