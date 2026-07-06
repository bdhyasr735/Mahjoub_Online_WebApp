# coding: utf-8
# 📂 apps/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy import MetaData

# تعريف الـ Naming Convention لمنع تعارض الأسماء
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

# ملاحظة: تم إزالة registered_modules من هنا 
# لأن العزل التام يقتضي عدم وجود قائمة مركزية مشتركة.

@login_manager.user_loader
def load_user(user_id):
    """
    دالة موحدة لتحميل المستخدمين.
    ملاحظة: تأكد من تمرير نوع المستخدم في الـ Session لزيادة دقة البحث.
    """
    from apps.models.admin_db import AdminUser
    from apps.models.supplier_db import Supplier
    from apps.models.supplier_staff_db import SupplierStaff
    from apps.models.marketer_db import Marketer
    
    try:
        uid = int(user_id)
        # التحقق من نوع المستخدم من الجلسة أولاً لتسريع الوصول (أمان إضافي)
        from flask import session
        user_type = session.get('user_type')
        
        if user_type == 'admin': return db.session.get(AdminUser, uid)
        if user_type == 'supplier': return db.session.get(Supplier, uid)
        if user_type == 'staff': return db.session.get(SupplierStaff, uid)
        if user_type == 'marketer': return db.session.get(Marketer, uid)
        
        # البحث الشامل في حال عدم وجود Session
        return db.session.get(Supplier, uid) or \
               db.session.get(SupplierStaff, uid) or \
               db.session.get(Marketer, uid) or \
               db.session.get(AdminUser, uid)
               
    except (ValueError, TypeError, Exception):
        return None

login_manager.login_view = 'auth_portal.login'
login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى لوحة التحكم."
login_manager.login_message_category = "info"
