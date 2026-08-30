# apps/forms/supplier/recovery_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp

class ForgotPasswordForm(FlaskForm):
    """نموذج طلب استعادة كلمة المرور"""
    identifier = StringField('المعرف', validators=[
        DataRequired(message='يرجى إدخال اسم المستخدم، البريد الإلكتروني، أو رقم الهاتف')
    ])


class ResetPasswordForm(FlaskForm):
    """نموذج إعادة تعيين كلمة المرور"""
    identifier = HiddenField('المعرف')
    user_type = HiddenField('نوع المستخدم', default='supplier')
    otp_code = StringField('رمز التحقق', validators=[
        DataRequired(message='يرجى إدخال رمز التحقق'),
        Length(min=6, max=6, message='رمز التحقق يجب أن يكون 6 أرقام'),
        Regexp(r'^\d{6}$', message='رمز التحقق يجب أن يحتوي على أرقام فقط')
    ])
    new_password = PasswordField('كلمة المرور الجديدة', validators=[
        DataRequired(message='يرجى إدخال كلمة المرور الجديدة'),
        Length(min=8, message='كلمة المرور يجب أن تكون 8 أحرف على الأقل')
    ])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(message='يرجى تأكيد كلمة المرور'),
        EqualTo('new_password', message='كلمتا المرور غير متطابقتين')
    ])
