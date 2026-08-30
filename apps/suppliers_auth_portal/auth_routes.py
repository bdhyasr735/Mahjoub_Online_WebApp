# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_routes.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from datetime import datetime, timedelta
import secrets

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet

# ✅ إنشاء البلوبرنت مع تحديد مجلد القوالب لحل مشكلة TemplateNotFound
bp = Blueprint('suppliers_auth', __name__, template_folder='templates')


# ============================================================
# 🟣 تسجيل الدخول
# ============================================================

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/suppliers/dashboard')  # ✅ مسار مباشر
    
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
        
        digits = ''.join(filter(str.isdigit, identifier))
        search_phone = digits[-9:] if len(digits) >= 9 else None
        
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
            return jsonify({'success': False, 'message': f'الحساب {user.status}'}), 403
        
        if not user.check_password(password):
            return jsonify({'success': False, 'message': 'بيانات الدخول غير صحيحة'}), 401
        
        login_user(user, remember=remember_me)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'redirect_url': '/suppliers/dashboard',  # ✅ مسار مباشر
            'user': {'id': user.id, 'username': user.username, 'user_type': user_type, 'status': user.status}
        })
        
    except Exception as e:
        current_app.logger.error(f'❌ خطأ في تسجيل الدخول: {str(e)}')
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ في الخادم'}), 500


# ============================================================
# 🟣 تسجيل الخروج
# ============================================================

@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    username = current_user.username
    logout_user()
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect('/suppliers/login')  # ✅ مسار مباشر


# ============================================================
# 🟣 التسجيل
# ============================================================

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/suppliers/dashboard')
    
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
        
        wallet = SupplierWallet(
            supplier_id=supplier.id,
            wallet_code=f"WEL-963{supplier.id}",
            balance=0.0,
            status='active'
        )
        db.session.add(wallet)
        
        otp_code = generate_otp()
        session['verify_supplier_id'] = supplier.id
        session['verify_otp'] = otp_code
        
        db.session.commit()
        
        login_user(supplier)
        
        return jsonify({
            'success': True,
            'message': 'تم التسجيل بنجاح',
            'redirect_url': '/suppliers/verify',  # ✅ مسار مباشر
            'data': {'_dev_otp': otp_code}
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'خطأ في التسجيل: {str(e)}')
        return jsonify({'success': False, 'message': 'حدث خطأ في الخادم'}), 500


# ============================================================
# 🟣 استعادة كلمة المرور
# ============================================================

@bp.route('/forgot-password', methods=['GET'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect('/suppliers/dashboard')
    return render_template('suppliers_auth_portal/forgot_password.html')


@bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
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


@bp.route('/reset-password', methods=['POST'])
def reset_password():
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
            'redirect_url': '/suppliers/login'  # ✅ مسار مباشر
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 التحقق من الحساب
# ============================================================

@bp.route('/verify', methods=['GET', 'POST'])
def verify():
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
                'redirect_url': '/suppliers/dashboard'  # ✅ مسار مباشر
            })
        
        return jsonify({'success': False, 'message': 'لم يتم العثور على الحساب'}), 404
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 دوال مساعدة
# ============================================================

def generate_otp():
    return ''.join(secrets.choice('0123456789') for _ in range(6))


def extract_phone_digits(value):
    if not value:
        return None
    digits = ''.join(filter(str.isdigit, str(value)))
    return digits[-9:] if len(digits) >= 9 else digits


def get_user_by_identifier(identifier):
    supplier = Supplier.query.filter(
        or_(
            Supplier.username == identifier,
            Supplier.email == identifier,
            Supplier.search_phone == extract_phone_digits(identifier)
        )
    ).first()
    if supplier:
        return {'user': supplier, 'type': 'supplier'}
    
    staff = SupplierStaff.query.filter(
        or_(
            SupplierStaff.username == identifier,
            SupplierStaff.search_phone == extract_phone_digits(identifier)
        )
    ).first()
    if staff:
        return {'user': staff, 'type': 'employee'}
    
    if '@' in identifier:
        all_staff = SupplierStaff.query.all()
        for staff in all_staff:
            if staff.email and staff.email == identifier:
                return {'user': staff, 'type': 'employee'}
    
    return None


def store_otp(identifier, otp_code):
    otp_storage[identifier] = {
        'code': otp_code,
        'created_at': datetime.utcnow(),
        'attempts': 0,
        'max_attempts': 5
    }


def verify_otp(identifier, otp_code):
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
    if identifier in otp_storage:
        del otp_storage[identifier]


otp_storage = {}
