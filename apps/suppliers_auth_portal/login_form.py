# apps/forms/supplier/login_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    """نموذج تسجيل الدخول للموردين وموظفيهم"""
    identifier = StringField('المعرف', validators=[
        DataRequired(message='يرجى إدخال اسم المستخدم، البريد الإلكتروني، أو رقم الهاتف')
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message='يرجى إدخال كلمة المرور'),
        Length(min=8, message='كلمة المرور يجب أن تكون 8 أحرف على الأقل')
    ])
    user_type = HiddenField('نوع المستخدم', default='supplier')
    remember_me = BooleanField('تذكر بيانات الدخول', default=False)
