# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_register.py
# محرك التسجيل - يدعم تسجيل الموردين الجدد مع تشفير متكامل

import secrets
import re
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for, current_app
from flask_login import login_user, current_user
from sqlalchemy import or_

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet

# إنشاء بلو برنت
bp = Blueprint('auth_register', __name__)


# ============================================================
# دوال مساعدة
# ============================================================

def extract_phone_digits(value):
    """استخراج آخر 9 أرقام من قيمة نصية"""
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


def is_phone_unique(phone):
    """التحقق من عدم وجود رقم الهاتف مسبقاً"""
    if not phone:
        return True
    search_phone = extract_phone_digits(phone)
    if not search_phone:
        return True
    
    if Supplier.query.filter_by(search_phone=search_phone).first():
        return False
    if SupplierStaff.query.filter_by(search_phone=search_phone).first():
        return False
    return True


def is_username_unique(username):
    """التحقق من عدم وجود اسم المستخدم مسبقاً"""
    if not username:
        return True
    if Supplier.query.filter_by(username=username).first():
        return False
    if SupplierStaff.query.filter_by(username=username).first():
        return False
    return True


def is_email_unique(email):
    """التحقق من عدم وجود البريد الإلكتروني مسبقاً"""
    if not email:
        return True
    if Supplier.query.filter_by(email=email).first():
        return False
    all_staff = SupplierStaff.query.all()
    for staff in all_staff:
        if staff.email and staff.email == email:
            return False
    return True


def generate_otp():
    """توليد رمز تحقق عشوائي مكون من 6 أرقام"""
    return ''.join(secrets.choice('0123456789') for _ in range(6))


# ============================================================
# المسارات
# ============================================================

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة تسجيل مورد جديد"""
    if current_user.is_authenticated:
        return redirect(url_for('supplier.dashboard'))
    
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/register.html')
    
    # POST - معالجة التسجيل
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
        
        # التحقق من البيانات المطلوبة
        if not all([trade_name, owner_name, username, phone, password]):
            return jsonify({
                'success': False,
                'message': 'يرجى ملء جميع الحقول المطلوبة'
            }), 400
        
        if not agree:
            return jsonify({
                'success': False,
                'message': 'يجب الموافقة على شروط حوكمة الأسعار'
            }), 400
        
        # التحقق من عدم تكرار اسم المستخدم
        if not is_username_unique(username):
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم موجود مسبقاً'
            }), 400
        
        # التحقق من صحة رقم الهاتف
        if not validate_phone(phone):
            return jsonify({
                'success': False,
                'message': 'رقم الهاتف يجب أن يحتوي على 9 أرقام على الأقل'
            }), 400
        
        # التحقق من عدم تكرار رقم الهاتف
        if not is_phone_unique(phone):
            return jsonify({
                'success': False,
                'message': 'رقم الهاتف مسجل مسبقاً'
            }), 400
        
        # التحقق من عدم تكرار البريد الإلكتروني
        if email and not is_email_unique(email):
            return jsonify({
                'success': False,
                'message': 'البريد الإلكتروني مسجل مسبقاً'
            }), 400
        
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
            wallet_code=generate_wallet_code(supplier.id),
            balance=0.0,
            status='active'
        )
        db.session.add(wallet)
        
        # توليد OTP للتحقق
        otp_code = generate_otp()
        session['verify_supplier_id'] = supplier.id
        session['verify_otp'] = otp_code
        
        db.session.commit()
        
        # طباعة OTP في السجلات
        current_app.logger.info(f'🔐 OTP للمورد {username}: {otp_code}')
        print(f'🔐 OTP للمورد {username}: {otp_code}')
        
        # تسجيل الدخول التلقائي
        login_user(supplier)
        
        return jsonify({
            'success': True,
            'message': 'تم التسجيل بنجاح. تم إرسال رمز التحقق.',
            'redirect_url': url_for('auth_recovery.verify', identifier=username),
            'data': {
                'supplier_id': supplier.id,
                'username': supplier.username,
                'supplier_code': supplier.supplier_code,
                'wallet_code': wallet.wallet_code,
                'status': supplier.status,
                '_dev_otp': otp_code
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'خطأ في التسجيل: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في الخادم. يرجى المحاولة مرة أخرى.'
        }), 500


@bp.route('/register/check-username', methods=['POST'])
def check_username():
    """التحقق من توفر اسم المستخدم (AJAX)"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'available': False, 'message': 'يرجى إدخال اسم المستخدم'}), 400
        
        if len(username) < 3:
            return jsonify({'available': False, 'message': 'اسم المستخدم يجب أن يكون 3 أحرف على الأقل'}), 400
        
        is_available = is_username_unique(username)
        
        return jsonify({
            'available': is_available,
            'message': 'اسم المستخدم متاح' if is_available else 'اسم المستخدم غير متاح'
        })
        
    except Exception as e:
        current_app.logger.error(f'خطأ في التحقق من اسم المستخدم: {str(e)}')
        return jsonify({'available': False, 'message': 'حدث خطأ أثناء التحقق'}), 500


@bp.route('/register/check-phone', methods=['POST'])
def check_phone():
    """التحقق من توفر رقم الهاتف (AJAX)"""
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        
        if not phone:
            return jsonify({'available': False, 'message': 'يرجى إدخال رقم الهاتف'}), 400
        
        if not validate_phone(phone):
            return jsonify({'available': False, 'message': 'رقم الهاتف يجب أن يحتوي على 9 أرقام'}), 400
        
        is_available = is_phone_unique(phone)
        
        return jsonify({
            'available': is_available,
            'message': 'رقم الهاتف متاح' if is_available else 'رقم الهاتف مسجل مسبقاً'
        })
        
    except Exception as e:
        current_app.logger.error(f'خطأ في التحقق من رقم الهاتف: {str(e)}')
        return jsonify({'available': False, 'message': 'حدث خطأ أثناء التحقق'}), 500


@bp.route('/register/check-email', methods=['POST'])
def check_email():
    """التحقق من توفر البريد الإلكتروني (AJAX)"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'available': True, 'message': 'البريد الإلكتروني اختياري'})
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'available': False, 'message': 'صيغة البريد الإلكتروني غير صحيحة'}), 400
        
        is_available = is_email_unique(email)
        
        return jsonify({
            'available': is_available,
            'message': 'البريد الإلكتروني متاح' if is_available else 'البريد الإلكتروني مسجل مسبقاً'
        })
        
    except Exception as e:
        current_app.logger.error(f'خطأ في التحقق من البريد الإلكتروني: {str(e)}')
        return jsonify({'available': False, 'message': 'حدث خطأ أثناء التحقق'}), 500


# ============================================================
# معالج الأخطاء
# ============================================================

@bp.errorhandler(400)
def bad_request_error(error):
    if request.is_json:
        return jsonify({'success': False, 'message': 'طلب غير صالح'}), 400
    flash('طلب غير صالح', 'danger')
    return redirect(url_for('auth_register.register'))


@bp.errorhandler(500)
def internal_error(error):
    if request.is_json:
        return jsonify({'success': False, 'message': 'حدث خطأ داخلي في الخادم'}), 500
    flash('حدث خطأ داخلي في الخادم', 'danger')
    return redirect(url_for('auth_register.register'))
