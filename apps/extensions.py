# coding: utf-8
# 📂 apps/extensions.py - إعداد الإضافات المركزية

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import MetaData
from sqlalchemy.orm import joinedload
from flask import session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# تعريف الـ Naming Convention لمنع تعارض الأسماء في قاعدة البيانات
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

limiter = Limiter(
    key_func=get_remote_address, 
    default_limits=["5000 per day", "1000 per hour"],
    storage_uri="memory://"
)

@login_manager.user_loader
def load_user(user_id):
    try:
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.supplier_staff_db import SupplierStaff
        from apps.models.marketer_db import Marketer
        
        uid = int(user_id)
        user_type = session.get('user_type')
        
        if user_type == 'staff':
            return SupplierStaff.query.options(joinedload(SupplierStaff.supplier)).get(uid)
            
        if user_type == 'admin': return db.session.get(AdminUser, uid)
        if user_type == 'supplier': return db.session.get(Supplier, uid)
        if user_type == 'marketer': return db.session.get(Marketer, uid)
        
        return (db.session.get(Supplier, uid) or 
                db.session.get(SupplierStaff, uid) or 
                db.session.get(Marketer, uid) or 
                db.session.get(AdminUser, uid))
                
    except (ValueError, TypeError, Exception):
        return None

# ✅ إعدادات تسجيل الدخول - تم التصحيح
login_manager.login_view = 'suppliers_auth_bp.login'  # ✅ صحيح
login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى لوحة التحكم."
login_manager.login_message_category = "info"
