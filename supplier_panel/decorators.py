from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def sovereign_approval_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # التأكد أن المستخدم مسجل دخول وله بروفايل مورد معتمد
        if not current_user.is_authenticated or \
           current_user.role != 'supplier' or \
           not current_user.supplier_profile or \
           not current_user.supplier_profile.is_approved:
            
            flash('عذراً، هذه المنطقة تتطلب تعميداً سيادياً نشطاً.', 'danger')
            return redirect(url_for('supplier_panel.login'))
            
        return f(*args, **kwargs)
    return decorated_function
