# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/routes.py
# باك اند بوابة الموردين - مثل admin_suppliers_list تماماً

import secrets
from datetime import datetime, timedelta
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import or_

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet

# ✅ إنشاء الـ Blueprint
suppliers_auth_bp = Blueprint(
    'suppliers_auth',
    __name__,
    template_folder='templates'
)

# ============================================================
# 🟣 تخزين OTP مؤقت
# ============================================================
otp_storage = {}


# ============================================================
# 🟣 دوال مساعدة
# ============================================================

def extract_phone_digits(value):
    """استخراج آخر 9 أرقام من رقم الهاتف"""
    if not value:
        return None
    digits = ''.join(filter(str.isdigit, str(value)))
    return digits[-9:] if len(digits) >= 9 else digits


def generate_otp():
    """توليد رمز تحقق عشوائي مكون من 6 أرقام"""
    return ''.join(secrets.choice('0123456789') for _ in range(6))


def get_user_by_identifier(identifier):
    """البحث عن مستخدم (مورد أو موظف) بواسطة المعرف"""
    # البحث في الموردين
    supplier = Supplier.query.filter(
        or_(
            Supplier.username == identifier,
            Supplier.email == identifier,
            Supplier.search_phone == extract_phone_digits(identifier)
        )
    ).first()
    if supplier:
        return {'user': supplier, 'type': 'supplier'}
    
    # البحث في موظفي الموردين
    staff = SupplierStaff.query.filter(
        or_(
            SupplierStaff.username == identifier,
            SupplierStaff.search_phone == extract_phone_digits(identifier)
        )
    ).first()
    if staff:
        return {'user': staff, 'type': 'employee'}
    
    # البحث بالبريد الإلكتروني (للموظفين)
    if '@' in identifier:
        all_staff = SupplierStaff.query.all()
        for staff in all_staff:
            if staff.email and staff.email == identifier:
                return {'user': staff, 'type': 'employee'}
    
    return None


def store_otp(identifier, otp_code):
    """تخزين OTP مع وقت الإنشاء"""
    otp_storage[identifier] = {
        'code': otp_code,
        'created_at': datetime.utcnow(),
        'attempts': 0,
        'max_attempts': 5
    }


def verify_otp(identifier, otp_code):
    """التحقق من صحة OTP"""
    if identifier not in otp_storage:
        return False
    stored = otp_storage[identifier]
    if stored['attempts'] >= stored['max_attempts']:
        return False
    if datetime.utcnow() - stored['created_at'] > timedelta(minutes=10):
        return False
    if stored['code'] != otp_code:
        stored['attempts'] += 1
        return False
    return True


def clear_otp(identifier):
    """حذف OTP بعد الاستخدام"""
    if identifier in otp_storage:
        del otp_storage[identifier]


# ============================================================
# 🟣 مسار تسجيل الدخول
# ============================================================

@suppliers_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if current_user.is_authenticated:
        return redirect(url_for('suppliers_dashboard.dashboard'))
    
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/login.html')
    
    # POST: معالجة تسجيل الدخول
    try:
        data = request.get_json() or request.form
        identifier = data.get('identifier', '').strip()
        password = data.get('password', '')
        user_type = data.get('user_type', 'supplier')
        remember_me = data.get('remember_me', False)
        
        if not identifier or not password:
            return jsonify({'success': False, 'message': 'يرجى إدخال جميع البيانات'}), 400
        
        search_phone = extract_phone_digits(identifier)
        user = None
        
        if user_type == 'supplier':
            user = Supplier.query.filter(
                or_(
                    Supplier.username == identifier,
                    Supplier.email == identifier,
                    Supplier.search_phone == search_phone
                )
            ).first()
        elif user_type == 'employee':
            user = SupplierStaff.query.filter(
                or_(
                    SupplierStaff.username == identifier,
                    SupplierStaff.search_phone == search_phone
                )
            ).first()
            if not user and '@' in identifier:
                all_staff = SupplierStaff.query.all()
                for staff in all_staff:
                    if staff.email and staff.email == identifier:
                        user = staff
                        break
        else:
            return jsonify({'success': False, 'message': 'نوع المستخدم غير مدعوم'}), 400
        
        if not user:
            return jsonify({'success': False, 'message': 'بيانات الدخول غير صحيحة'}), 401
        
        if user.status != 'active':
            status_messages = {
                'inactive': 'الحساب غير نشط',
                'suspended': 'الحساب موقوف مؤقتاً',
                'pending': 'الحساب في انتظار التفعيل'
            }
            return jsonify({'success': False, 'message': status_messages.get(user.status, 'الحساب غير متاح')}), 403
        
        if not user.check_password(password):
            return jsonify({'success': False, 'message': 'بيانات الدخول غير صحيحة'}), 401
        
        login_user(user, remember=remember_me)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'redirect_url': url_for('suppliers_dashboard.dashboard'),
            'user': {
                'id': user.id,
                'username': user.username,
                'user_type': user_type,
                'status': user.status
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 مسار تسجيل الخروج
# ============================================================

@suppliers_auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """تسجيل الخروج"""
    username = current_user.username
    logout_user()
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('suppliers_auth.login'))


# ============================================================
# 🟣 مسار التسجيل
# ============================================================

@suppliers_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة تسجيل مورد جديد"""
    if current_user.is_authenticated:
        return redirect(url_for('suppliers_dashboard.dashboard'))
    
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/register.html')
    
    # POST: معالجة التسجيل
    try:
        data = request.get_json() or request.form
        
        trade_name = data.get('trade_name', '').strip()
        owner_name = data.get('owner_name', '').strip()
        username = data.get('username', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip() or None
        store_name = data.get('store_name', '').strip() or trade_name
        password = data.get('password', '')
        agree = data.get('agree_pricing_policy', False)
        
        if not all([trade_name, owner_name, username, phone, password]):
            return jsonify({'success': False, 'message': 'يرجى ملء جميع الحقول المطلوبة'}), 400
        
        if not agree:
            return jsonify({'success': False, 'message': 'يجب الموافقة على شروط حوكمة الأسعار'}), 400
        
        if Supplier.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'اسم المستخدم موجود مسبقاً'}), 400
        
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 9:
            return jsonify({'success': False, 'message': 'رقم الهاتف يجب أن يحتوي على 9 أرقام'}), 400
        
        search_phone = digits[-9:]
        if Supplier.query.filter_by(search_phone=search_phone).first():
            return jsonify({'success': False, 'message': 'رقم الهاتف مسجل مسبقاً'}), 400
        
        if email and Supplier.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'البريد الإلكتروني مسجل مسبقاً'}), 400
        
        # إنشاء المورد
        supplier = Supplier(
            username=username,
            email=email,
            owner_name=owner_name,
            trade_name=trade_name,
            store_name=store_name,
            status='pending'
        )
        supplier.phone = phone
        supplier.set_password(password)
        
        db.session.add(supplier)
        db.session.flush()
        
        # إنشاء المحفظة
        wallet = SupplierWallet(
            supplier_id=supplier.id,
            wallet_code=f"WEL-963{supplier.id}",
            balance=0.0,
            status='active'
        )
        db.session.add(wallet)
        
        # توليد OTP للتحقق
        otp_code = generate_otp()
        session['verify_supplier_id'] = supplier.id
        session['verify_otp'] = otp_code
        
        db.session.commit()
        
        # تسجيل الدخول التلقائي
        login_user(supplier)
        
        return jsonify({
            'success': True,
            'message': 'تم التسجيل بنجاح',
            'redirect_url': url_for('suppliers_auth.verify', identifier=username),
            'data': {
                'supplier_id': supplier.id,
                'username': supplier.username,
                '_dev_otp': otp_code
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 مسار استعادة كلمة المرور
# ============================================================

@suppliers_auth_bp.route('/forgot-password', methods=['GET'])
def forgot_password():
    """صفحة استعادة كلمة المرور"""
    if current_user.is_authenticated:
        return redirect(url_for('suppliers_dashboard.dashboard'))
    return render_template('suppliers_auth_portal/forgot_password.html')


@suppliers_auth_bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """طلب إرسال OTP"""
    try:
        data = request.get_json() or request.form
        identifier = data.get('identifier', '').strip()
        
        if not identifier:
            return jsonify({'success': False, 'message': 'يرجى إدخال المعرف'}), 400
        
        user_data = get_user_by_identifier(identifier)
        if not user_data:
            return jsonify({'success': False, 'message': 'لم يتم العثور على الحساب'}), 404
        
        otp_code = generate_otp()
        store_otp(identifier, otp_code)
        session['recovery_identifier'] = identifier
        
        return jsonify({
            'success': True,
            'message': 'تم إرسال رمز التحقق',
            'data': {'_dev_otp': otp_code}
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@suppliers_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """إعادة تعيين كلمة المرور"""
    try:
        data = request.get_json() or request.form
        identifier = data.get('identifier', '').strip()
        otp_code = data.get('otp_code', '').strip()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not identifier or not otp_code or not new_password:
            return jsonify({'success': False, 'message': 'يرجى إدخال جميع البيانات'}), 400
        
        if len(otp_code) != 6:
            return jsonify({'success': False, 'message': 'رمز التحقق يجب أن يكون 6 أرقام'}), 400
        
        if len(new_password) < 8:
            return jsonify({'success': False, 'message': 'كلمة المرور يجب أن تكون 8 أحرف على الأقل'}), 400
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'كلمتا المرور غير متطابقتين'}), 400
        
        if not verify_otp(identifier, otp_code):
            return jsonify({'success': False, 'message': 'رمز التحقق غير صحيح'}), 401
        
        user_data = get_user_by_identifier(identifier)
        if not user_data:
            return jsonify({'success': False, 'message': 'لم يتم العثور على الحساب'}), 404
        
        user = user_data['user']
        user.set_password(new_password)
        if user.status == 'pending':
            user.status = 'active'
        
        db.session.commit()
        clear_otp(identifier)
        session.pop('recovery_identifier', None)
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث كلمة المرور بنجاح',
            'redirect_url': url_for('suppliers_auth.login')
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 مسار التحقق من الحساب
# ============================================================

@suppliers_auth_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    """صفحة التحقق من الحساب"""
    if request.method == 'GET':
        identifier = request.args.get('identifier', '')
        return render_template('suppliers_auth_portal/verify.html', identifier=identifier)
    
    try:
        data = request.get_json() or request.form
        otp_code = data.get('otp_code', '').strip()
        
        if not otp_code or len(otp_code) != 6:
            return jsonify({'success': False, 'message': 'يرجى إدخال رمز التحقق'}), 400
        
        stored_otp = session.get('verify_otp')
        supplier_id = session.get('verify_supplier_id')
        
        if not stored_otp or not supplier_id:
            return jsonify({'success': False, 'message': 'انتهت صلاحية الجلسة'}), 401
        
        if stored_otp != otp_code:
            return jsonify({'success': False, 'message': 'رمز التحقق غير صحيح'}), 401
        
        supplier = Supplier.query.get(supplier_id)
        if supplier:
            supplier.status = 'active'
            db.session.commit()
            session.pop('verify_otp', None)
            session.pop('verify_supplier_id', None)
            
            return jsonify({
                'success': True,
                'message': 'تم التحقق من الحساب بنجاح',
                'redirect_url': url_for('suppliers_dashboard.dashboard')
            })
        
        return jsonify({'success': False, 'message': 'لم يتم العثور على الحساب'}), 404
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 مسار الملف الشخصي (JSON)
# ============================================================

@suppliers_auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """عرض ملف المورد الشخصي (JSON)"""
    try:
        if isinstance(current_user, Supplier):
            supplier = current_user
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
            
            return jsonify({
                'success': True,
                'supplier': {
                    'id': supplier.id,
                    'username': supplier.username,
                    'email': supplier.email,
                    'supplier_code': supplier.supplier_code,
                    'owner_name': supplier.owner_name,
                    'trade_name': supplier.trade_name,
                    'store_name': supplier.store_name,
                    'phone': supplier.phone,
                    'status': supplier.status,
                    'rank': supplier.rank,
                    'wallet_code': wallet.wallet_code if wallet else None,
                    'balance': float(wallet.balance) if wallet else 0
                }
            })
        
        return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 مسار تحديث الملف الشخصي
# ============================================================

@suppliers_auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """تحديث بيانات الملف الشخصي"""
    try:
        if not isinstance(current_user, Supplier):
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        supplier = current_user
        data = request.get_json() or request.form
        
        # تحديث الحقول المسموح بها
        if 'trade_name' in data:
            supplier.trade_name = data['trade_name'].strip()
        if 'store_name' in data:
            supplier.store_name = data['store_name'].strip()
        if 'email' in data:
            supplier.email = data['email'].strip()
        if 'phone' in data:
            supplier.phone = data['phone'].strip()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث الملف الشخصي بنجاح',
            'supplier': {
                'id': supplier.id,
                'username': supplier.username,
                'email': supplier.email,
                'trade_name': supplier.trade_name,
                'store_name': supplier.store_name,
                'phone': supplier.phone
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 مسار المحفظة (JSON)
# ============================================================

@suppliers_auth_bp.route('/wallet', methods=['GET'])
@login_required
def wallet():
    """عرض بيانات المحفظة (JSON)"""
    try:
        if isinstance(current_user, Supplier):
            supplier = current_user
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
            
            if not wallet:
                return jsonify({'success': False, 'message': 'لا توجد محفظة'}), 404
            
            return jsonify({
                'success': True,
                'wallet': {
                    'id': wallet.id,
                    'wallet_code': wallet.wallet_code,
                    'balance': float(wallet.balance),
                    'currency': wallet.currency,
                    'status': wallet.status,
                    'created_at': wallet.created_at.isoformat() if wallet.created_at else None,
                    'updated_at': wallet.updated_at.isoformat() if wallet.updated_at else None
                }
            })
        
        return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 معالج الأخطاء
# ============================================================

@suppliers_auth_bp.errorhandler(404)
def not_found_error(error):
    if request.is_json:
        return jsonify({'success': False, 'message': 'الصفحة غير موجودة'}), 404
    flash('الصفحة غير موجودة', 'danger')
    return redirect(url_for('suppliers_auth.login'))


@suppliers_auth_bp.errorhandler(500)
def internal_error(error):
    if request.is_json:
        return jsonify({'success': False, 'message': 'حدث خطأ في الخادم'}), 500
    flash('حدث خطأ في الخادم', 'danger')
    return redirect(url_for('suppliers_auth.login'))
