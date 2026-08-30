# apps/suppliers_auth_portal/routes.py

"""
مسارات المصادقة والتحكم في بوابة الموردين وموظفيهم
يعتمد على النماذج الموجودة في apps/models
"""

import logging
import re
import random
import string
import os
import requests
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_profile_db import SupplierProfile
from apps.models.wallet_db import SupplierWallet
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.product_supplier_map import ProductSupplierMapping

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

def send_whatsapp_otp(phone, otp_code):
    """إرسال رمز التحقق عبر واتساب باستخدام Meta Cloud API الرسمي"""
    try:
        formatted_phone = validate_phone(phone)
        if not formatted_phone:
            return False
            
        phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '1336881386166971')
        access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        
        if not access_token:
            logger.error("❌ رمز الوصول WHATSAPP_ACCESS_TOKEN غير متوفر في متغيرات البيئة")
            return False

        url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        if not formatted_phone.startswith('967') and len(formatted_phone) == 9:
            recipient_phone = f"967{formatted_phone}"
        else:
            recipient_phone = formatted_phone

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_phone,
            "type": "text",
            "text": {
                "body": f"رمز التحقق الخاص بك في منصة محجوب أونلاين هو: *{otp_code}*\nصالح لمدة 10 دقائق."
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"📲 تم إرسال رمز الواتساب بنجاح عبر ميتا إلى الرقم: {recipient_phone}")
            return True
        else:
            logger.error(f"❌ فشل إرسال واتساب من ميتا: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ خطأ غير متوقع أثناء إرسال واتساب: {str(e)}", exc_info=True)
        return False


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
            return jsonify({'success': False, 'message': 'يرجى إدخال اسم المستخدم أو البريد أو الهاتف وكلمة المرور'}), 400

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
    """صفحة تسجيل مورد جديد"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('suppliers_auth_bp.dashboard'))
        return render_template('suppliers_auth_portal/register.html', page_title='اشتراك مورد جديد')
    except Exception as e:
        logger.error(f"❌ خطأ في عرض صفحة التسجيل: {str(e)}", exc_info=True)
        return f"Internal Server Error: {str(e)}", 500


@suppliers_auth_bp.route('/check-availability', methods=['POST'])
def check_availability():
    """التحقق اللحظي من قاعدة البيانات لتوفر (اسم المستخدم، البريد، أو الهاتف)"""
    try:
        data = request.get_json(silent=True) or {}
        field = data.get('field')
        value = str(data.get('value', '')).strip()

        if not field or not value:
            return jsonify({'available': True})

        if field == 'username':
            valid_val = validate_username(value)
            if not valid_val:
                return jsonify({'available': False, 'message': 'اسم المستخدم غير صالح'})
            exists = Supplier.query.filter_by(username=valid_val).first() or SupplierStaff.query.filter_by(username=valid_val).first()
        elif field == 'email':
            valid_val = validate_email(value)
            if not valid_val:
                return jsonify({'available': False, 'message': 'البريد الإلكتروني غير صالح'})
            exists = Supplier.query.filter_by(email=valid_val).first() or SupplierStaff.query.filter_by(email=valid_val).first()
        elif field == 'phone':
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
    """معالجة تسجيل مورد جديد"""
    try:
        data = request.get_json(silent=True) or request.form
        if not data:
            return jsonify({'success': False, 'message': 'بيانات غير صالحة'}), 400

        username = str(data.get('username', '')).strip()
        email = str(data.get('email', '')).strip()
        phone = str(data.get('phone', '')).strip()
        password = str(data.get('password', ''))
        confirm_password = str(data.get('confirm_password', ''))
        trade_name = str(data.get('trade_name', '')).strip()
        store_name = str(data.get('store_name', '')).strip()
        full_address = str(data.get('full_address', '')).strip()
        city = str(data.get('city', '')).strip()
        district = str(data.get('district', '')).strip()

        if not all([username, email, phone, password, confirm_password]):
            return jsonify({'success': False, 'message': 'جميع الحقول الأساسية مطلوبة'}), 400

        if password != confirm_password:
            return jsonify({'success': False, 'message': 'كلمتا المرور غير متطابقتين'}), 400

        if len(password) < 8:
            return jsonify({'success': False, 'message': 'كلمة المرور يجب أن تكون 8 أحرف على الأقل'}), 400

        valid_email = validate_email(email)
        valid_phone = validate_phone(phone)
        valid_username = validate_username(username)

        if not valid_email or not valid_phone or not valid_username:
            return jsonify({'success': False, 'message': 'أحد المدخلات (البريد، الهاتف، أو اسم المستخدم) غير صالح'}), 400

        if Supplier.query.filter_by(email=valid_email).first():
            return jsonify({'success': False, 'message': 'البريد الإلكتروني مستخدم بالفعل'}), 409

        if Supplier.query.filter_by(phone=valid_phone).first() or Supplier.query.filter_by(search_phone=valid_phone).first():
            return jsonify({'success': False, 'message': 'رقم الهاتف مستخدم بالفعل'}), 409

        if Supplier.query.filter_by(username=valid_username).first():
            return jsonify({'success': False, 'message': 'اسم المستخدم مستخدم بالفعل'}), 409

        new_supplier = Supplier(
            username=valid_username,
            email=valid_email,
            phone=phone,
            search_phone=valid_phone,
            owner_name=trade_name or store_name or valid_username,
            trade_name=trade_name,
            store_name=store_name or trade_name or valid_username,
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

        profile = SupplierProfile(
            supplier_id=new_supplier.id,
            full_address=full_address,
            city=city,
            district=district
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
            'message': 'تم إنشاء حساب المورد بنجاح',
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


# دعم كلا المسارين (سواء بوجود s أو بدونها لتجنب خطأ 404 تماماً)
@suppliers_auth_bp.route('/forgot-password/request-otp', methods=['POST'])
@suppliers_auth_bp.route('/supplier/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """طلب رمز التحقق OTP عبر الواتساب"""
    try:
        data = request.get_json(silent=True) or request.form
        identifier = str(data.get('identifier', '')).strip()
        if not identifier:
            return jsonify({'success': False, 'message': 'يرجى إدخال المعرف'}), 400

        user, user_type = find_user(identifier)
        if not user:
            return jsonify({'success': False, 'message': 'الحساب غير موجود'}), 404

        target_phone = getattr(user, 'phone', None)
        if not target_phone:
            return jsonify({'success': False, 'message': 'لا يوجد رقم هاتف مسجل لهذا الحساب لإرسال رمز الواتساب'}), 400

        otp_code = generate_otp()
        whatsapp_sent = send_whatsapp_otp(target_phone, otp_code)
        
        if not whatsapp_sent:
            return jsonify({'success': False, 'message': 'فشل إرسال رمز التحقق عبر واتساب، يرجى المحاولة لاحقاً'}), 500

        session['reset_otp'] = {
            'code': otp_code,
            'identifier': identifier,
            'user_type': user_type,
            'user_id': user.id,
            'expires_at': (datetime.now() + timedelta(minutes=10)).isoformat()
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

        stored_otp_data = session.get('reset_otp')
        if not stored_otp_data:
            return jsonify({'success': False, 'message': 'انتهت صلاحية الجلسة أو لم يتم طلب رمز تحقق'}), 400

        expires_at = datetime.fromisoformat(stored_otp_data['expires_at'])
        if datetime.now() > expires_at:
            session.pop('reset_otp', None)
            return jsonify({'success': False, 'message': 'انتهت صلاحية رمز التحقق، يرجى طلب رمز جديد'}), 400

        if stored_otp_data['code'] != otp_code:
            return jsonify({'success': False, 'message': 'رمز التحقق غير صحيح'}), 400

        user_id = stored_otp_data['user_id']
        u_type = stored_otp_data['user_type']

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
        session.pop('reset_otp', None)

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
    """لوحة التحكم الرئيسية"""
    try:
        user_type = session.get('user_type', 'supplier')
        
        if user_type == 'supplier' and hasattr(current_user, 'id'):
            supplier_id = current_user.id
            products_count = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id, is_active=True).count()
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
            balance = wallet.balance if wallet else 0.0
            staff_count = SupplierStaff.query.filter_by(supplier_id=supplier_id, is_active=True).count()
            profile = SupplierProfile.query.filter_by(supplier_id=supplier_id).first()
            
            return render_template(
                'suppliers_auth_portal/dashboard/supplier_dashboard.html',
                page_title='لوحة تحكم المورد',
                user=current_user,
                profile=profile,
                wallet=wallet,
                products_count=products_count,
                staff_count=staff_count,
                balance=balance
            )
        
        return render_template(
            'suppliers_auth_portal/dashboard/employee_dashboard.html',
            page_title='لوحة تحكم موظف المورد',
            user=current_user
        )
    except Exception as e:
        logger.error(f"❌ خطأ في لوحة التحكم: {str(e)}", exc_info=True)
        return f"Dashboard Error: {str(e)}", 500


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
    
    logger.info("✅ تم تهيئة بوابة مصادقة الموردين بنجاح مع تفعيل نظام التقاط الأخطاء ومسارات الاستعادة")
    return app
