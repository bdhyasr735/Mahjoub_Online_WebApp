# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/auth_login.py
# محرك تسجيل الدخول - يدعم الموردين وموظفي الموردين مع تشفير متكامل

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from sqlalchemy import or_
import re
from datetime import datetime, timedelta

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.forms.supplier.login_form import LoginForm

# إنشاء بلو برنت
bp = Blueprint('auth_login', __name__, url_prefix='/supplier')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    صفحة تسجيل الدخول - تدعم كلاً من:
    - الموردين (Supplier)
    - موظفي الموردين (SupplierStaff)
    """
    # إذا كان المستخدم مسجل دخول بالفعل، إعادة توجيهه للوحة التحكم
    if current_user.is_authenticated:
        return redirect(url_for('supplier.dashboard'))
    
    form = LoginForm()
    
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/login.html', form=form)
    
    # POST: معالجة تسجيل الدخول
    if not form.validate_on_submit():
        return jsonify({
            'success': False,
            'message': 'بيانات الدخول غير صالحة',
            'errors': form.errors
        }), 400
    
    identifier = form.identifier.data.strip()
    password = form.password.data
    user_type = form.user_type.data
    remember_me = form.remember_me.data
    
    # البحث عن المستخدم بناءً على نوعه
    user = None
    user_model = None
    
    try:
        if user_type == 'supplier':
            user_model = Supplier
            # البحث في عدة حقول (اسم المستخدم، البريد الإلكتروني، رقم الهاتف)
            user = Supplier.query.filter(
                or_(
                    Supplier.username == identifier,
                    Supplier.email == identifier,
                    Supplier.search_phone == extract_phone_digits(identifier)
                )
            ).first()
        elif user_type == 'employee':
            user_model = SupplierStaff
            # البحث في عدة حقول مع مراعاة التشفير
            # ملاحظة: البحث بالبريد الإلكتروني المشفر يتطلب معالجة خاصة
            user = SupplierStaff.query.filter(
                or_(
                    SupplierStaff.username == identifier,
                    SupplierStaff.search_phone == extract_phone_digits(identifier)
                )
            ).first()
            
            # إذا لم يتم العثور عليه بالبريد المشفر، نبحث بشكل منفصل
            if not user and '@' in identifier:
                # فك تشفير جميع البريدات والبحث (قد يكون بطيئاً مع البيانات الكبيرة)
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
            # تسجيل محاولة فاشلة (للمراقبة)
            current_app.logger.warning(f'محاولة دخول فاشلة: {identifier} - نوع: {user_type}')
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'
            }), 401
        
        # التحقق من حالة الحساب
        if user.status == 'inactive':
            return jsonify({
                'success': False,
                'message': 'الحساب غير نشط. يرجى التواصل مع الدعم الفني.'
            }), 403
        
        if user.status == 'suspended':
            return jsonify({
                'success': False,
                'message': 'الحساب موقوف مؤقتاً. يرجى التواصل مع الدعم الفني.'
            }), 403
        
        if user.status == 'pending':
            return jsonify({
                'success': False,
                'message': 'الحساب في انتظار التفعيل. يرجى التحقق من بريدك الإلكتروني أو هاتفك.'
            }), 403
        
        # التحقق من كلمة المرور
        if not user.check_password(password):
            # تسجيل محاولة فاشلة
            current_app.logger.warning(f'محاولة دخول فاشلة (كلمة مرور خاطئة): {identifier}')
            
            # تحديث عدد المحاولات الفاشلة (يمكن إضافة حقل لهذا الغرض)
            return jsonify({
                'success': False,
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'
            }), 401
        
        # نجاح تسجيل الدخول
        login_user(user, remember=remember_me)
        
        # تحديث وقت آخر تسجيل دخول
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # تسجيل نجاح الدخول
        current_app.logger.info(f'تسجيل دخول ناجح: {user.username} - نوع: {user_type} - ID: {user.id}')
        
        # تحديد صفحة الوجهة
        redirect_url = request.args.get('next') or url_for('supplier.dashboard')
        
        return jsonify({
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'redirect_url': redirect_url,
            'user': {
                'id': user.id,
                'username': user.username,
                'user_type': user_type,
                'status': user.status
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'خطأ في تسجيل الدخول: {str(e)}')
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'حدث خطأ أثناء معالجة طلب الدخول. يرجى المحاولة مرة أخرى.'
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


@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    لوحة تحكم المورد/الموظف
    تعرض إحصائيات أساسية وروابط سريعة
    """
    # التحقق من نوع المستخدم
    if isinstance(current_user, Supplier):
        user_type = 'supplier'
        # جلب إحصائيات المورد
        stats = {
            'total_orders': len(current_user.orders) if current_user.orders else 0,
            'total_products': 0,  # سيتم جلبها من ProductSupplierMapping
            'total_staff': len(current_user.staff_members) if current_user.staff_members else 0,
            'wallet_balance': current_user.wallet.balance if current_user.wallet else 0
        }
    elif isinstance(current_user, SupplierStaff):
        user_type = 'employee'
        stats = {
            'supplier_name': current_user.supplier.trade_name if current_user.supplier else 'غير محدد',
            'role': current_user.role,
            'total_orders': 0,  # سيتم جلبها من الطلبات المرتبطة بالموظف
            'total_products': 0
        }
    else:
        flash('نوع المستخدم غير معروف', 'danger')
        return redirect(url_for('auth_login.login'))
    
    return render_template(
        'supplier/dashboard.html',
        user=current_user,
        user_type=user_type,
        stats=stats
    )


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    عرض وتحديث الملف الشخصي للمستخدم
    """
    if request.method == 'GET':
        if isinstance(current_user, Supplier):
            return render_template('supplier/profile.html', user=current_user, user_type='supplier')
        else:
            return render_template('supplier/profile.html', user=current_user, user_type='employee')
    
    # POST: تحديث الملف الشخصي (سيتم تنفيذه لاحقاً)
    return jsonify({'success': False, 'message': 'قيد التطوير'}), 501


# ==================== دوال مساعدة ====================

def extract_phone_digits(value):
    """
    استخراج آخر 9 أرقام من قيمة نصية للبحث في search_phone
    """
    if not value:
        return None
    
    # استخراج الأرقام فقط
    digits = ''.join(filter(str.isdigit, str(value)))
    
    # إرجاع آخر 9 أرقام
    return digits[-9:] if len(digits) >= 9 else digits


def get_user_by_identifier(identifier, user_type='supplier'):
    """
    البحث عن مستخدم بواسطة المعرف (اسم المستخدم، البريد، أو رقم الهاتف)
    """
    if user_type == 'supplier':
        return Supplier.query.filter(
            or_(
                Supplier.username == identifier,
                Supplier.email == identifier,
                Supplier.search_phone == extract_phone_digits(identifier)
            )
        ).first()
    else:
        return SupplierStaff.query.filter(
            or_(
                SupplierStaff.username == identifier,
                SupplierStaff.search_phone == extract_phone_digits(identifier)
            )
        ).first()


# ==================== معالج الأخطاء ====================

@bp.errorhandler(401)
def unauthorized_error(error):
    """معالج خطأ المصادقة"""
    if request.is_json:
        return jsonify({'success': False, 'message': 'يرجى تسجيل الدخول أولاً'}), 401
    flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
    return redirect(url_for('auth_login.login'))


@bp.errorhandler(403)
def forbidden_error(error):
    """معالج خطأ عدم الصلاحية"""
    if request.is_json:
        return jsonify({'success': False, 'message': 'لا تملك صلاحية للوصول إلى هذه الصفحة'}), 403
    flash('لا تملك صلاحية للوصول إلى هذه الصفحة', 'danger')
    return redirect(url_for('auth_login.dashboard'))
