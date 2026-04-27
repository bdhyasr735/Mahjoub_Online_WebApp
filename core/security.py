from functools import wraps
from flask import abort, redirect, url_for, flash, session
from flask_login import current_user

def admin_required(f):
    """حارس بوابة الإدارة: يسمح فقط لمن لديه رتبة admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("عذراً، هذه المنطقة تتطلب صلاحيات قيادية عليا.", "danger")
            return abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def supplier_required(f):
    """حارس بوابة الموردين: يسمح فقط لمن لديه رتبة supplier"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'supplier':
            flash("هذه البوابة مخصصة للموردين المعتمدين فقط.", "warning")
            return redirect(url_for('supplier_panel.login'))
        return f(*args, **kwargs)
    return decorated_function

def sovereign_approval_required(f):
    """
    شرط التعميد السيادي: 
    يمنع المورد من دخول اللوحة حتى لو كان حسابه صحيحاً، 
    ما لم يتم تفعيل حالته (is_approved) من قبل علي محجوب.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # التأكد أولاً أنه مورد
        if current_user.role == 'supplier':
            # التحقق من وجود بروفايل وحالة الموافقة
            if not current_user.supplier_profile or not current_user.supplier_profile.is_approved:
                flash("حسابك قيد المراجعة السيادية. سيتم تفعيل الدخول فور التعميد.", "info")
                # يمكن توجيهه لصفحة "قيد الانتظار" أو تسجيل خروجه
                return redirect(url_for('supplier_panel.login'))
        
        return f(*args, **kwargs)
    return decorated_function
