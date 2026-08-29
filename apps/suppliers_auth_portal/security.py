from functools import wraps
from flask import session, jsonify, redirect, url_for, flash
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.suppliers_auth_portal.registry import EMPLOYEE_ROLES

def supplier_login_required(f):
    """ديكوراتور للتحقق من أن المستخدم مسجل دخول (سواء مورد أساسي أو موظف)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        user_type = session.get('user_type')
        
        if not user_id or user_type not in ['supplier', 'employee']:
            flash('❌ يجب تسجيل الدخول للوصول إلى هذه الصفحة', 'danger')
            return redirect(url_for('suppliers_auth_bp.login'))
            
        # التحقق من حالة المستخدم في القاعدة
        if user_type == 'supplier':
            user = Supplier.query.get(user_id)
        else:
            user = SupplierStaff.query.get(user_id)
            
        if not user or getattr(user, 'status', 'active') != 'active':
            session.clear()
            flash('❌ الحساب موقوف أو غير صالح', 'danger')
            return redirect(url_for('suppliers_auth_bp.login'))
            
        return f(*args, **kwargs)
    return decorated_function

def permission_required(required_permission):
    """ديكوراتور للتحقق مما إذا كان المورد أو الموظف يمتلك الصلاحية المطلوبة"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            user_type = session.get('user_type')
            
            if not user_id or user_type not in ['supplier', 'employee']:
                return jsonify({"success": False, "message": "غير مصرح لك بالوصول"}), 403
                
            # إذا كان المستخدم هو المورد الأساسي (Owner)، فهو يمتلك كافة الصلاحيات تلقائياً
            if user_type == 'supplier':
                return f(*args, **kwargs)
                
            # إذا كان موظفاً، نتحقق من صلاحيات دوره المعرف في EMPLOYEE_ROLES
            staff = SupplierStaff.query.get(user_id)
            if not staff or staff.status != 'active':
                return jsonify({"success": False, "message": "حساب موظف غير فعال"}), 403
                
            staff_role = staff.role  # مثال: 'sales', 'accountant', 'manager'
            role_info = EMPLOYEE_ROLES.get(staff_role, {})
            allowed_permissions = role_info.get("permissions", [])
            
            # التحقق هل الصلاحية المطلوبة ضمن صلاحيات دور الموظف
            if required_permission not in allowed_permissions:
                return jsonify({
                    "success": False, 
                    "message": f"عذراً، ليس لديك الصلاحية المطلوبة ({required_permission})"
                }), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
