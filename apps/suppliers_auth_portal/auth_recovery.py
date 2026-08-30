# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_recovery.py
# محرك استعادة كلمة المرور - يدعم الموردين وموظفي الموردين مع OTP

import secrets
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for, current_app
from flask_login import current_user
from sqlalchemy import or_

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff

# إنشاء بلو برنت
bp = Blueprint('auth_recovery', __name__)

# ============================================================
# تخزين OTP مؤقت
# ============================================================
otp_storage = {}


def generate_otp():
    """توليد رمز تحقق عشوائي مكون من 6 أرقام"""
    return ''.join(secrets.choice('0123456789') for _ in range(6))


def extract_phone_digits(value):
    """استخراج آخر 9 أرقام من قيمة نصية"""
    if not value:
        return None
    digits = ''.join(filter(str.isdigit, str(value)))
    return digits[-9:] if len(digits) >= 9 else digits


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
    
    # البحث بالبريد الإلكتروني المشفر للموظفين
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


def mask_identifier(identifier):
    """إخفاء جزء من المعرف للعرض"""
    if not identifier:
        return identifier
    
    if '@' in identifier:
        parts = identifier.split('@')
        if len(parts[0]) > 2:
            masked = parts[0][:2] + '***' + parts[0][-1:]
        else:
            masked = parts[0][:1] + '***'
        return f"{masked}@{parts[1]}"
    
    digits = ''.join(filter(str.isdigit, identifier))
    if len(digits) >= 9:
        return f"{digits[:3]}****{digits[-2:]}"
    
    if len(identifier) > 3:
        return f"{identifier[:2]}***{identifier[-1:]}"
    
    return identifier


# ============================================================
# المسارات
# ============================================================

@bp.route('/forgot-password', methods=['GET'])
def forgot_password():
    """صفحة استعادة كلمة المرور"""
    if current_user.is_authenticated:
        return redirect(url_for('supplier.dashboard'))
    
    return render_template('suppliers_auth_portal/forgot_password.html')


@bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """طلب إرسال OTP"""
    try:
        data = request.get_json() or request.form
        identifier = data.get('identifier', '').strip()
        
        if not identifier:
            return jsonify({
                'success': False,
                'message': 'يرجى إدخال اسم المستخدم، رقم الهاتف، أو البريد الإلكتروني'
            }), 400
        
        user_data = get_user_by_identifier(identifier)
        if not user_data:
            current_app.logger.warning(f'محاولة استعادة كلمة مرور لحساب غير موجود: {identifier}')
            return jsonify({
                'success': False,
                'message': 'لم يتم العثور على حساب مرتبط بالبيانات المدخلة'
            }), 404
        
        user = user_data['user']
        user_type = user_data['type']
        
        if user.status == 'inactive':
            return jsonify({
                'success': False,
                'message': 'الحساب غير نشط. يرجى التواصل مع الدعم الفني.'
            }), 403
        
        otp_code = generate_otp()
        store_otp(identifier, otp_code)
        
        session['recovery_identifier'] = identifier
        session['recovery_user_type'] = user_type
        
        # طباعة OTP في السجلات (للتطوير)
        current_app.logger.info(f'🔐 OTP لاستعادة كلمة المرور لـ {identifier}: {otp_code}')
        print(f'🔐 OTP لاستعادة كلمة المرور لـ {identifier}: {otp_code}')
        
        return jsonify({
            'success': True,
            'message': 'تم إرسال رمز التحقق',
            'data': {
                'masked_identifier': mask_identifier(identifier),
                '_dev_otp': otp_code
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'خطأ في طلب OTP: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في الخادم. يرجى المحاولة مرة أخرى.'
        }), 500


@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """إعادة تعيين كلمة المرور باستخدام OTP"""
    try:
        data = request.get_json() or request.form
        
        identifier = data.get('identifier', '').strip()
        otp_code = data.get('otp_code', '').strip()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not identifier:
            return jsonify({'success': False, 'message': 'يرجى إدخال المعرف'}), 400
        
        if not otp_code or len(otp_code) != 6:
            return jsonify({'success': False, 'message': 'يرجى إدخال رمز التحقق المكون من 6 أرقام'}), 400
        
        if not new_password or len(new_password) < 8:
            return jsonify({'success': False, 'message': 'كلمة المرور يجب أن تكون 8 أحرف على الأقل'}), 400
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'كلمتا المرور غير متطابقتين'}), 400
        
        if not verify_otp(identifier, otp_code):
            return jsonify({'success': False, 'message': 'رمز التحقق غير صحيح أو انتهت صلاحيته'}), 401
        
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
        session.pop('recovery_user_type', None)
        
        current_app.logger.info(f'✅ تم إعادة تعيين كلمة المرور لـ {user.username}')
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث كلمة المرور بنجاح',
            'redirect_url': url_for('auth_login.login')
        })
        
    except Exception as e:
        current_app.logger.error(f'خطأ في إعادة تعيين كلمة المرور: {str(e)}')
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في الخادم. يرجى المحاولة مرة أخرى.'
        }), 500


@bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """إعادة إرسال OTP"""
    try:
        data = request.get_json() or request.form
        identifier = data.get('identifier', '').strip()
        
        if not identifier:
            identifier = session.get('recovery_identifier')
            if not identifier:
                return jsonify({
                    'success': False,
                    'message': 'لم يتم العثور على المعرف. يرجى بدء عملية الاستعادة من جديد.'
                }), 400
        
        user_data = get_user_by_identifier(identifier)
        if not user_data:
            return jsonify({'success': False, 'message': 'لم يتم العثور على الحساب'}), 404
        
        otp_code = generate_otp()
        store_otp(identifier, otp_code)
        
        current_app.logger.info(f'🔐 إعادة إرسال OTP لـ {identifier}: {otp_code}')
        print(f'🔐 إعادة إرسال OTP لـ {identifier}: {otp_code}')
        
        return jsonify({
            'success': True,
            'message': 'تم إعادة إرسال رمز التحقق',
            'data': {'_dev_otp': otp_code}
        })
        
    except Exception as e:
        current_app.logger.error(f'خطأ في إعادة إرسال OTP: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في الخادم. يرجى المحاولة مرة أخرى.'
        }), 500


@bp.route('/verify', methods=['GET', 'POST'])
def verify():
    """صفحة التحقق من الحساب"""
    if request.method == 'GET':
        identifier = request.args.get('identifier', '')
        return render_template('suppliers_auth_portal/verify.html', identifier=identifier)
    
    try:
        data = request.get_json() or request.form
        otp_code = data.get('otp_code', '').strip()
        
        if not otp_code or len(otp_code) != 6:
            return jsonify({'success': False, 'message': 'يرجى إدخال رمز التحقق المكون من 6 أرقام'}), 400
        
        stored_otp = session.get('verify_otp')
        supplier_id = session.get('verify_supplier_id')
        
        if not stored_otp or not supplier_id:
            return jsonify({'success': False, 'message': 'انتهت صلاحية جلسة التحقق'}), 401
        
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
                'redirect_url': url_for('supplier.dashboard')
            })
        
        return jsonify({'success': False, 'message': 'لم يتم العثور على الحساب'}), 404
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'خطأ في التحقق: {str(e)}')
        return jsonify({'success': False, 'message': 'حدث خطأ في الخادم'}), 500
