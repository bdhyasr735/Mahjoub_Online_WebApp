# apps/forms/supplier/register_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, ValidationError
import re

from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff


class RegisterForm(FlaskForm):
    """نموذج تسجيل مورد جديد"""
    
    trade_name = StringField('اسم المنشأة', validators=[
        DataRequired(message='يرجى إدخال اسم المنشأة'),
        Length(min=3, max=150, message='اسم المنشأة يجب أن يكون بين 3 و 150 حرفاً')
    ])
    
    owner_name = StringField('اسم المالك', validators=[
        DataRequired(message='يرجى إدخال اسم المالك'),
        Length(min=3, max=150, message='اسم المالك يجب أن يكون بين 3 و 150 حرفاً')
    ])
    
    username = StringField('اسم المستخدم', validators=[
        DataRequired(message='يرجى إدخال اسم المستخدم'),
        Length(min=3, max=100, message='اسم المستخدم يجب أن يكون بين 3 و 100 حرفاً'),
        Regexp(r'^[a-zA-Z0-9_.-]+$', message='اسم المستخدم يحتوي على أحرف غير مسموحة')
    ])
    
    phone = StringField('رقم الهاتف', validators=[
        DataRequired(message='يرجى إدخال رقم الهاتف'),
        Length(min=9, max=20, message='رقم الهاتف يجب أن يكون بين 9 و 20 رقماً')
    ])
    
    email = EmailField('البريد الإلكتروني', validators=[
        Email(message='صيغة البريد الإلكتروني غير صحيحة'),
        Length(max=120, message='البريد الإلكتروني طويل جداً')
    ])
    
    store_name = StringField('اسم المتجر', validators=[
        Length(max=150, message='اسم المتجر طويل جداً')
    ])
    
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message='يرجى إدخال كلمة المرور'),
        Length(min=8, message='كلمة المرور يجب أن تكون 8 أحرف على الأقل')
    ])
    
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(message='يرجى تأكيد كلمة المرور'),
        EqualTo('password', message='كلمتا المرور غير متطابقتين')
    ])
    
    category = SelectField('فئة النشاط', choices=[
        ('', 'اختر فئة التوريد الرئيسية...'),
        ('food', 'المواد الغذائية والتموينية الأساسية'),
        ('electronics', 'الأجهزة الإلكترونية والتقنية'),
        ('clothing', 'الملابس والمنسوجات'),
        ('wholesale', 'تجارة الجملة العامة والمستلزمات'),
        ('other', 'أخرى / منتجات متخصصة')
    ], validators=[
        DataRequired(message='يرجى اختيار فئة النشاط')
    ])
    
    agree_pricing_policy = BooleanField('الموافقة على سياسة التسعير', validators=[
        DataRequired(message='يجب الموافقة على شروط حوكمة الأسعار')
    ])
    
    def validate_username(self, field):
        """التحقق من عدم وجود اسم المستخدم مسبقاً"""
        if Supplier.query.filter_by(username=field.data).first():
            raise ValidationError('اسم المستخدم موجود مسبقاً')
        if SupplierStaff.query.filter_by(username=field.data).first():
            raise ValidationError('اسم المستخدم موجود مسبقاً')
    
    def validate_phone(self, field):
        """التحقق من صحة رقم الهاتف وعدم تكراره"""
        # استخراج الأرقام فقط
        digits = ''.join(filter(str.isdigit, field.data))
        if len(digits) < 9:
            raise ValidationError('رقم الهاتف يجب أن يحتوي على 9 أرقام على الأقل')
        
        # استخراج آخر 9 أرقام
        search_phone = digits[-9:] if len(digits) >= 9 else digits
        
        # التحقق من عدم التكرار
        if Supplier.query.filter_by(search_phone=search_phone).first():
            raise ValidationError('رقم الهاتف مسجل مسبقاً')
        if SupplierStaff.query.filter_by(search_phone=search_phone).first():
            raise ValidationError('رقم الهاتف مسجل مسبقاً')
    
    def validate_email(self, field):
        """التحقق من عدم وجود البريد الإلكتروني مسبقاً"""
        if field.data:
            if Supplier.query.filter_by(email=field.data).first():
                raise ValidationError('البريد الإلكتروني مسجل مسبقاً')
            # التحقق من بريد الموظفين (فك التشفير)
            all_staff = SupplierStaff.query.all()
            for staff in all_staff:
                if staff.email and staff.email == field.data:
                    raise ValidationError('البريد الإلكتروني مسجل مسبقاً')
