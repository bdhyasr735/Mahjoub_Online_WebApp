from flask import flash
from flask_login import login_user
from core.models.user import User

def handle_supplier_auth(username, password):
    # البحث عن المورد فقط
    user = User.query.filter_by(username=username, role='supplier').first()
    
    if not user:
        flash('تنبيه: هذا الحساب غير مسجل في المنصة اللامركزية للموردين.', 'error')
        return None

    # التحقق من الهوية (محجوب أونلاين | 123) أو عبر القاعدة
    if (username == "محجوب أونلاين" and password == "123") or user.check_password(password):
        login_user(user)
        return user
    else:
        flash('خطأ في كلمة المرور، حاول مرة أخرى.', 'error')
        return None
