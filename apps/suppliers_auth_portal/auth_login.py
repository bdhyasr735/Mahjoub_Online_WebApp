# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_login.py
# محرك تسجيل الدخول - يدعم الموردين وموظفي الموردين مع تشفير متكامل

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from datetime import datetime

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff

# إنشاء بلو برنت
bp = Blueprint('auth_login', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    صفحة تسجيل الدخول - تدعم كلاً من:
    - الموردين (Supplier)
    - موظفي الموردين (SupplierStaff)
    """
    # إذا كان المستخدم مسجل دخول بالفعل
    if current_user.is_authenticated:
        # ✅ التحويل إلى لوحة تحكم الموردين
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
            return jsonify({
                'success': False,
                'message': 'يرجى إدخال جميع البيانات'
            }), 400
        
        # البحث عن المستخدم
        user = None
        search_phone = extract_phone_digits(identifier)
        
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
            
            # البحث بالبريد الإلكتروني (مشفر)
            if not user and '@' in identifier:
                all_staff = SupplierStaff.query.all()
                for staff in all_staff:
                    if staff.email and staff.email == identifier:
                        user = staff
                        break
        else:
            return jsonify({
                'success': False,
                'message': 'نوع المستخدم غير مدعوم'
            }), 400
        
        # التحقق من وجود المستخدم
        if not user:
            current_app.logger.warning(f'محاولة دخول فاشلة: {identifier}')
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'
            }), 401
        
        # التحقق من حالة الحساب
        if user.status != 'active':
            status_messages = {
                'inactive': 'الحساب غير نشط. يرجى التواصل مع الدعم الفني.',
                'suspended': 'الحساب موقوف مؤقتاً. يرجى التواصل مع الدعم الفني.',
                'pending': 'الحساب في انتظار التفعيل. يرجى التحقق من بريدك الإلكتروني أو هاتفك.'
            }
            return jsonify({
                'success': False,
                'message': status_messages.get(user.status, 'الحساب غير متاح')
            }), 403
        
        # التحقق من كلمة المرور
        if not user.check_password(password):
            current_app.logger.warning(f'كلمة مرور خاطئة: {identifier}')
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'
            }), 401
        
        # ✅ نجاح تسجيل الدخول
        login_user(user, remember=remember_me)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f'✅ تسجيل دخول ناجح: {user.username}')
        
        # ✅ التحويل إلى لوحة تحكم الموردين
        return jsonify({
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'redirect_url': request.args.get('next') or url_for('suppliers_dashboard.dashboard'),
            'user': {
                'id': user.id,
                'username': user.username,
                'user_type': user_type,
                'status': user.status
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'❌ خطأ في تسجيل الدخول: {str(e)}')
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في الخادم. يرجى المحاولة مرة أخرى.'
        }), 500


@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """تسجيل الخروج من النظام"""
    username = current_user.username
    logout_user()
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    current_app.logger.info(f'تسجيل خروج: {username}')
    return redirect(url_for('auth_login.login'))


# ==================== دوال مساعدة ====================

def extract_phone_digits(value):
    """استخراج آخر 9 أرقام من قيمة نصية للبحث في search_phone"""
    if not value:
        return None
    digits = ''.join(filter(str.isdigit, str(value)))
    return digits[-9:] if len(digits) >= 9 else digits


def get_user_by_identifier(identifier, user_type='supplier'):
    """البحث عن مستخدم بواسطة المعرف"""
    search_phone = extract_phone_digits(identifier)
    
    if user_type == 'supplier':
        return Supplier.query.filter(
            or_(
                Supplier.username == identifier,
                Supplier.email == identifier,
                Supplier.search_phone == search_phone
            )
        ).first()
    else:
        return SupplierStaff.query.filter(
            or_(
                SupplierStaff.username == identifier,
                SupplierStaff.search_phone == search_phone
            )
        ).first()


# ==================== معالج الأخطاء ====================

@bp.errorhandler(401)
def unauthorized_error(error):
    if request.is_json:
        return jsonify({'success': False, 'message': 'يرجى تسجيل الدخول أولاً'}), 401
    flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
    return redirect(url_for('auth_login.login'))


@bp.errorhandler(403)
def forbidden_error(error):
    if request.is_json:
        return jsonify({'success': False, 'message': 'لا تملك صلاحية للوصول'}), 403
    flash('لا تملك صلاحية للوصول إلى هذه الصفحة', 'danger')
    return redirect(url_for('auth_login.login'))
