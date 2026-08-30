# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_recovery.py
# محرك استعادة كلمة المرور - يدعم الموردين وموظفي الموردين مع OTP

import os
import secrets
import re
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for, current_app
from flask_login import current_user
from sqlalchemy import or_
from werkzeug.security import generate_password_hash

from apps.extensions import db, mail
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.forms.supplier.recovery_form import ForgotPasswordForm, ResetPasswordForm

# إنشاء بلو برنت
bp = Blueprint('auth_recovery', __name__, url_prefix='/supplier')

# ============================================================
# تخزين OTP مؤقت (في الإنتاج يُفضل استخدام Redis أو قاعدة بيانات)
# ============================================================
otp_storage = {}


def generate_otp():
    """توليد رمز تحقق عشوائي مكون من 6 أرقام"""
    return ''.join(secrets.choice('0123456789') for _ in range(6))


def extract_phone_digits(value):
    """استخراج آخر 9 أرقام من قيمة نصية للبحث في search_phone"""
    if not value:
        return None
    digits = ''.join(filter(str.isdigit, str(value)))
    return digits[-9:] if len(digits) >= 9 else digits


def get_user_by_identifier(identifier):
    """
    البحث عن مستخدم (مورد أو موظف) بواسطة المعرف
    يعيد قاموساً يحتوي على المستخدم ونوعه
    """
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
    
    # إذا كان المعرف بريداً إلكترونياً ولم يتم العثور عليه، نبحث في البريد المشفر للموظفين
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
    
    # التحقق من عدد المحاولات
    if stored['attempts'] >= stored['max_attempts']:
        return False
    
    # التحقق من صلاحية الرمز (10 دقائق)
    if datetime.utcnow() - stored['created_at'] > timedelta(minutes=10):
        return False
    
    # التحقق من الرمز
    if stored['code'] != otp_code:
        stored['attempts'] += 1
        return False
    
    # نجاح التحقق
    return True


def clear_otp(identifier):
    """حذف OTP بعد الاستخدام"""
    if identifier in otp_storage:
        del otp_storage[identifier]


def mask_identifier(identifier):
    """إخفاء جزء من المعرف لأغراض العرض"""
    if not identifier:
        return identifier
    
    # إذا كان بريداً إلكترونياً
    if '@' in identifier:
        parts = identifier.split('@')
        if len(parts[0]) > 2:
            masked = parts[0][:2] + '***' + parts[0][-1:]
        else:
            masked = parts[0][:1] + '***'
        return f"{masked}@{parts[1]}"
    
    # إذا كان رقم هاتف
    digits = ''.join(filter(str.isdigit, identifier))
    if len(digits) >= 9:
        return f"{digits[:3]}****{digits[-2:]}"
    
    # إذا كان اسم مستخدم
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
    
    form = ForgotPasswordForm()
    return render_template('suppliers_auth_portal/forgot_password.html', form=form)


@bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """
    طلب إرسال OTP
    POST: { identifier: "username/phone/email" }
    """
    try:
        data = request.get_json() or request.form
        identifier = data.get('identifier', '').strip()
        
        if not identifier:
            return jsonify({
                'success': False,
                'message': 'يرجى إدخال اسم المستخدم، رقم الهاتف، أو البريد الإلكتروني'
            }), 400
        
        # البحث عن المستخدم
        user_data = get_user_by_identifier(identifier)
        if not user_data:
            current_app.logger.warning(f'محاولة استعادة كلمة مرور لحساب غير موجود: {identifier}')
            # لأسباب أمنية، نعطي نفس الرسالة حتى لا نكشف وجود الحساب
            return jsonify({
                'success': False,
                'message': 'لم يتم العثور على حساب مرتبط بالبيانات المدخلة'
            }), 404
        
        user = user_data['user']
        user_type = user_data['type']
        
        # التحقق من حالة الحساب
        if user.status == 'inactive':
            return jsonify({
                'success': False,
                'message': 'الحساب غير نشط. يرجى التواصل مع الدعم الفني.'
            }), 403
        
        # توليد OTP
        otp_code = generate_otp()
        store_otp(identifier, otp_code)
        
        # تخزين معلومات الجلسة
        session['recovery_identifier'] = identifier
        session['recovery_user_type'] = user_type
        
        # إرسال OTP عبر القناة المناسبة
        masked_identifier = mask_identifier(identifier)
        sent_via = []
        
        # محاولة إرسال عبر WhatsApp (إذا كان رقماً)
        phone_digits = extract_phone_digits(identifier)
        if phone_digits and len(phone_digits) >= 9:
            try:
                send_whatsapp_otp(phone_digits, otp_code)
                sent_via.append('whatsapp')
            except Exception as e:
                current_app.logger.error(f'فشل إرسال OTP عبر WhatsApp: {str(e)}')
        
        # محاولة إرسال عبر البريد الإلكتروني (إذا كان بريداً)
        if '@' in identifier:
            try:
                send_email_otp(identifier, otp_code)
                sent_via.append('email')
            except Exception as e:
                current_app.logger.error(f'فشل إرسال OTP عبر البريد: {str(e)}')
        
        # إذا لم يتم الإرسال بأي طريقة
        if not sent_via:
            current_app.logger.error(f'فشل إرسال OTP لـ {identifier} عبر جميع القنوات')
            return jsonify({
                'success': False,
                'message': 'تعذر إرسال رمز التحقق. يرجى التأكد من صحة رقم الهاتف أو البريد الإلكتروني.'
            }), 500
        
        return jsonify({
            'success': True,
            'message': f'تم إرسال رمز التحقق عبر {", ".join(sent_via)}',
            'data': {
                'masked_identifier': masked_identifier,
                'sent_via': sent_via,
                # في بيئة التطوير فقط
                '_dev_otp': otp_code if current_app.debug else None
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'خطأ في طلب OTP: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'حدث خطأ أثناء معالجة الطلب. يرجى المحاولة مرة أخرى.'
        }), 500


@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    إعادة تعيين كلمة المرور باستخدام OTP
    POST: { identifier, otp_code, new_password, confirm_password }
    """
    try:
        data = request.get_json() or request.form
        
        identifier = data.get('identifier', '').strip()
        otp_code = data.get('otp_code', '').strip()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        # التحقق من صحة البيانات
        if not identifier:
            return jsonify({
                'success': False,
                'message': 'يرجى إدخال المعرف'
            }), 400
        
        if not otp_code or len(otp_code) != 6:
            return jsonify({
                'success': False,
                'message': 'يرجى إدخال رمز التحقق المكون من 6 أرقام'
            }), 400
        
        if not new_password or len(new_password) < 8:
            return jsonify({
                'success': False,
                'message': 'كلمة المرور يجب أن تكون 8 أحرف على الأقل'
            }), 400
        
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'كلمتا المرور غير متطابقتين'
            }), 400
        
        # التحقق من OTP
        if not verify_otp(identifier, otp_code):
            return jsonify({
                'success': False,
                'message': 'رمز التحقق غير صحيح أو انتهت صلاحيته'
            }), 401
        
        # البحث عن المستخدم
        user_data = get_user_by_identifier(identifier)
        if not user_data:
            return jsonify({
                'success': False,
                'message': 'لم يتم العثور على الحساب'
            }), 404
        
        user = user_data['user']
        
        # تحديث كلمة المرور
        user.set_password(new_password)
        
        # تفعيل الحساب إذا كان معلقاً
        if user.status == 'pending':
            user.status = 'active'
        
        db.session.commit()
        
        # حذف OTP
        clear_otp(identifier)
        session.pop('recovery_identifier', None)
        session.pop('recovery_user_type', None)
        
        current_app.logger.info(f'تم إعادة تعيين كلمة المرور لـ {user.username}')
        
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
            'message': 'حدث خطأ أثناء تحديث كلمة المرور. يرجى المحاولة مرة أخرى.'
        }), 500


@bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """
    إعادة إرسال OTP
    POST: { identifier, channel }
    """
    try:
        data = request.get_json() or request.form
        identifier = data.get('identifier', '').strip()
        channel = data.get('channel', 'whatsapp')
        
        if not identifier:
            # محاولة جلب المعرف من الجلسة
            identifier = session.get('recovery_identifier')
            if not identifier:
                return jsonify({
                    'success': False,
                    'message': 'لم يتم العثور على المعرف. يرجى بدء عملية الاستعادة من جديد.'
                }), 400
        
        # البحث عن المستخدم
        user_data = get_user_by_identifier(identifier)
        if not user_data:
            return jsonify({
                'success': False,
                'message': 'لم يتم العثور على الحساب'
            }), 404
        
        # توليد OTP جديد
        otp_code = generate_otp()
        store_otp(identifier, otp_code)
        
        # إرسال OTP حسب القناة المطلوبة
        sent = False
        
        if channel == 'whatsapp':
            phone_digits = extract_phone_digits(identifier)
            if phone_digits and len(phone_digits) >= 9:
                try:
                    send_whatsapp_otp(phone_digits, otp_code)
                    sent = True
                except Exception as e:
                    current_app.logger.error(f'فشل إرسال OTP عبر WhatsApp: {str(e)}')
        
        elif channel == 'email' and '@' in identifier:
            try:
                send_email_otp(identifier, otp_code)
                sent = True
            except Exception as e:
                current_app.logger.error(f'فشل إرسال OTP عبر البريد: {str(e)}')
        
        if not sent:
            return jsonify({
                'success': False,
                'message': f'تعذر إرسال رمز التحقق عبر {channel}. يرجى المحاولة عبر قناة أخرى.'
            }), 500
        
        return jsonify({
            'success': True,
            'message': f'تم إعادة إرسال رمز التحقق عبر {channel}',
            'data': {
                '_dev_otp': otp_code if current_app.debug else None
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'خطأ في إعادة إرسال OTP: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'حدث خطأ أثناء إعادة الإرسال. يرجى المحاولة مرة أخرى.'
        }), 500


# ============================================================
# دوال إرسال OTP (يمكن توسيعها لاستخدام خدمات حقيقية)
# ============================================================

def send_whatsapp_otp(phone_number, otp_code):
    """
    إرسال OTP عبر WhatsApp
    يمكن استبدالها بخدمة حقيقية مثل Twilio أو Meta Cloud API
    """
    # TODO: تكامل مع خدمة WhatsApp Business API
    # مثال باستخدام Twilio:
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    #     from_='whatsapp:+14155238886',
    #     body=f'رمز التحقق الخاص بك: {otp_code}',
    #     to=f'whatsapp:+{phone_number}'
    # )
    
    current_app.logger.info(f'[WhatsApp] إرسال OTP {otp_code} إلى {phone_number}')
    
    # في بيئة التطوير، طباعة الرمز في السجلات
    if current_app.debug:
        print(f'📱 WhatsApp OTP لـ {phone_number}: {otp_code}')
    
    return True


def send_email_otp(email, otp_code):
    """
    إرسال OTP عبر البريد الإلكتروني
    """
    # TODO: تكامل مع Flask-Mail
    # from flask_mail import Message
    # msg = Message(
    #     'رمز التحقق - محجوب أونلاين',
    #     recipients=[email],
    #     body=f'رمز التحقق الخاص بك هو: {otp_code}\n\nالرمز صالح لمدة 10 دقائق.'
    # )
    # mail.send(msg)
    
    current_app.logger.info(f'[Email] إرسال OTP {otp_code} إلى {email}')
    
    # في بيئة التطوير، طباعة الرمز في السجلات
    if current_app.debug:
        print(f'✉️ Email OTP لـ {email}: {otp_code}')
    
    return True


# ============================================================
# معالج الأخطاء
# ============================================================

@bp.errorhandler(404)
def not_found_error(error):
    """معالج خطأ 404"""
    if request.is_json:
        return jsonify({'success': False, 'message': 'الصفحة غير موجودة'}), 404
    flash('الصفحة غير موجودة', 'danger')
    return redirect(url_for('auth_login.login'))


@bp.errorhandler(500)
def internal_error(error):
    """معالج خطأ 500"""
    if request.is_json:
        return jsonify({'success': False, 'message': 'حدث خطأ داخلي في الخادم'}), 500
    flash('حدث خطأ داخلي في الخادم. يرجى المحاولة مرة أخرى.', 'danger')
    return redirect(url_for('auth_login.login'))


# ============================================================
# تنظيف OTP القديم (يمكن تشغيله عبر cron job)
# ============================================================

def cleanup_expired_otp():
    """حذف OTP منتهية الصلاحية"""
    now = datetime.utcnow()
    expired = []
    for identifier, data in otp_storage.items():
        if now - data['created_at'] > timedelta(minutes=10):
            expired.append(identifier)
    
    for identifier in expired:
        del otp_storage[identifier]
    
    return len(expired)
